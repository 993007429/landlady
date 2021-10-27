import datetime
import enum
import pathlib
import shutil
import subprocess
import tarfile
import typing
from pathlib import Path
from typing import Optional, List

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError

from app.db.models.box import Box, BoxStatus
from app.domain.entities.box import BoxEntity
from app.domain.services.base import BaseService
from app.domain.services.errors import NewEntityFailException
from app.domain.utils.nginx import gen_nginx_conf
from app.domain.utils.supervisor import gen_supervisor_conf
from app.infra.repository import RepoQuery, PageParams
from app.domain.services import errors


class BoxOperation(enum.Enum):
    apply = '1'
    free = '2'


class BoxService(BaseService):

    def new_box(self, project_id: int, user_id: int, port_prefix: str, numprocs: int) -> BoxEntity:
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
                except FileNotFoundError:
                    pass

    def init_box(self, box: BoxEntity):
        Path(box.code_dir).mkdir(parents=True, exist_ok=True)
        Path(box.fe_dir).mkdir(parents=True, exist_ok=True)
        Path(box.logs_dir).mkdir(parents=True, exist_ok=True)
        gen_supervisor_conf(box)
        gen_nginx_conf(box)

    def get_box(self, box_id: int) -> Optional[BoxEntity]:
        box = self._repo_generator(Box).get(box_id)
        if not box:
            return None
        return self.entity_adapter.to_box_entity(box)

    def get_boxes_by_project(self, project_id: int, offset: int = 0, limit: int = 20) -> List[BoxEntity]:
        boxes = self._repo_generator(Box).get_models_by_query(
            RepoQuery(
                params={'project_id': project_id},
                order_by=[(Box.id, desc)],
                page_params=PageParams(offset=offset, limit=limit)
            )
        )
        return [self.entity_adapter.to_box_entity(box) for box in boxes if box]

    def check_project(self, box_project_id: int, project_id: int):
        if box_project_id != project_id:
            raise errors.WrongProjectException()

    def check_box_owner(self, box_ower_id: int, user_id: int):
        if not box_ower_id or box_ower_id != user_id:
            raise errors.WrongBoxException()

    def operate_box(self, box_id: int, project_id: int, user_id: int, operation: BoxOperation) -> Optional[BoxEntity]:
        repo = self._repo_generator(Box)
        box = repo.get(box_id)
        if not box:
            raise errors.EntityDoesNotExist(box_id)

        self.check_project(box.project_id, project_id)

        if operation == BoxOperation.apply:
            if box.user_id == user_id:
                return self.get_box(box_id)
            elif box.user_id:
                raise errors.BoxUnavailableException(box_id)
            box.user_id = user_id
        else:
            self.check_box_owner(box.user_id, user_id)
            box.user_id = 0

        repo.save(box)
        return self.get_box(box_id)

    def deploy_in_box(self, box_id: int, project_id: int, user_id: int, file: typing.IO) -> str:
        box = self.get_box(box_id)
        if not box:
            raise errors.EntityDoesNotExist(box_id)

        self.operate_box(box_id, project_id, user_id, BoxOperation.apply)

        self.check_project(box.project.id, project_id)

        shutil.rmtree(box.code_dir, ignore_errors=True)

        with tarfile.open(fileobj=file, mode='r:gz') as tar:
            tar.extractall(box.box_dir)

        subprocess.call(['sudo', 'supervisorctl', 'restart', f'{box.app_name}:'])

        output = subprocess.check_output(['sudo', 'supervisorctl', 'status', f'{box.app_name}:']).decode('utf-8')
        box = self._repo_generator(Box).get(box_id)
        if 'RUNNING' in output:
            box.status = BoxStatus.on
            box.start_time = datetime.datetime.now()
        elif 'FATAL' in output:
            box.status = BoxStatus.error
        self._repo_generator(Box).save(box)
        return output
