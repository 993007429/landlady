import datetime
import enum
import pathlib
import shutil
import subprocess
import tarfile
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.box import Box, BoxStatus
from app.domain.entities.box import BoxEntity
from app.domain.services import errors
from app.domain.services.base import BaseService
from app.domain.services.errors import NewEntityFailException
from app.domain.utils.file import gen_file_structure
from app.domain.utils.nginx import gen_nginx_conf
from app.domain.utils.supervisor import gen_supervisor_conf


class BoxOperation(enum.Enum):
    apply = '1'
    apply_fe = '2'
    free = '3'


class BoxService(BaseService):

    def new_box(self, project_id: int, user_id: int, port_prefix: int, numprocs: int) -> BoxEntity:
        try:
            box = Box(
                project_id=project_id,
                user_id=user_id,
                port_prefix=port_prefix,
                numprocs=numprocs,
                status=BoxStatus.off
            )
            self._repo_generator(Box).save(box)
            return self.entity_adapter.to_box_entity(box)
        except SQLAlchemyError as e:
            raise NewEntityFailException() from e

    def delete_box(self, box_id) -> bool:
        box = self._repo_generator(Box).get(box_id)
        if box:
            box_entity = self.entity_adapter.to_box_entity(box)
            deleted = self._repo_generator(Box).delete(box)
            if deleted:
                try:
                    shutil.rmtree(pathlib.Path(box_entity.box_dir))
                    return True
                except FileNotFoundError:
                    pass
        return False

    def init_box(self, box: BoxEntity):
        Path(box.code_dir).mkdir(parents=True, exist_ok=True)
        Path(box.fe_dist_dir).mkdir(parents=True, exist_ok=True)
        Path(box.logs_dir).mkdir(parents=True, exist_ok=True)
        gen_supervisor_conf(box)
        gen_nginx_conf(box)

    def get_box(self, box_id: int) -> Optional[BoxEntity]:
        box = self._repo_generator(Box).get(box_id)
        if not box:
            return None
        return self.entity_adapter.to_box_entity(box)

    def check_project(self, box_project_id: int, project_id: int):
        if box_project_id != project_id:
            raise errors.WrongProjectException()

    def check_box_owner(self, box_ower_id: int, user_id: int):
        if not box_ower_id or box_ower_id != user_id:
            raise errors.WrongBoxException()

    def operate_box(self, box_id: int, project_id: int, user_id: int, operation: BoxOperation,
                    force: bool = False) -> Optional[BoxEntity]:
        repo = self._repo_generator(Box)
        box = repo.get(box_id)
        if not box:
            raise errors.EntityDoesNotExist(box_id)

        self.check_project(box.project_id, project_id)

        if operation == BoxOperation.apply:
            if box.user_id == user_id:
                return self.get_box(box_id)
            elif box.user_id and not force:
                raise errors.BoxUnavailableException(box_id)
            box.user_id = user_id
        elif operation == BoxOperation.apply_fe:
            if box.fe_owner_id == user_id:
                return self.get_box(box_id)
            elif box.fe_owner_id and not force:
                raise errors.BoxUnavailableException(box_id)
            box.fe_owner_id = user_id
        elif operation == BoxOperation.free:
            if box.user_id == user_id:
                box.user_id = 0
            if box.fe_owner_id == user_id:
                box.fe_owner_id = 0

        repo.save(box)
        return self.get_box(box_id)

    def deploy_in_box(self, box_id: int, project_id: int, user_id: int, bundle: UploadFile) -> str:
        box = self.get_box(box_id)
        if not box:
            raise errors.EntityDoesNotExist(box_id)

        is_fe_bundle = bundle.filename.startswith(box.fe_dist_name)

        self.operate_box(box_id, project_id, user_id, BoxOperation.apply_fe if is_fe_bundle else BoxOperation.apply)

        self.check_project(box.project.id, project_id)

        with tarfile.open(fileobj=bundle.file, mode='r:gz') as tar:
            if is_fe_bundle:
                shutil.rmtree(box.fe_dist_dir, ignore_errors=True)
                tar.extractall(box.box_dir)
            else:
                shutil.rmtree(box.code_dir, ignore_errors=True)
                tar.extractall(box.code_dir)

        if not is_fe_bundle:
            output = f'supervisor status:\n{"-" * 50}\n'
            output += self._restart_supervisor(box)
            output += '\n\n'
        else:
            output = f'fe dir structure:\n{"-" * 50}\n'
            output += gen_file_structure(box.fe_dist_dir)
            output += '\n\n'
        return output

    def _restart_supervisor(self, box):
        subprocess.call(['sudo', 'supervisorctl', 'restart', f'{box.app_name}:'])

        output = subprocess.check_output(['sudo', 'supervisorctl', 'status', f'{box.app_name}:']).decode('utf-8')
        box = self._repo_generator(Box).get(box.id)
        if 'RUNNING' in output:
            box.status = BoxStatus.on
            box.start_time = datetime.datetime.now()
        elif 'FATAL' in output or 'BACKOFF' in output:
            box.status = BoxStatus.error
        self._repo_generator(Box).save(box)
        return output


    def list_files(self, box_id: int, path: str = ''):
        box = self.get_box(box_id)
        if not box:
            raise errors.EntityDoesNotExist(box_id)

        return subprocess.check_output(['ls', '-al', f'{box.box_dir}/{path}']).decode('utf-8')
