import shutil
import subprocess
import tarfile
from typing import Optional, List

from fastapi import UploadFile
from sqlalchemy import desc

from app.db.models import Box
from app.db.models.admin import Admin
from app.db.models.project import Project
from app.domain.entities.box import BoxEntity
from app.domain.entities.project import ProjectEntity
from app.domain.services import errors
from app.domain.services.base import BaseService
from app.domain.utils.nginx import gen_nginx_conf
from app.domain.utils.supervisor import gen_supervisor_conf
from app.infra.repository import RepoQuery, PageParams


class ProjectService(BaseService):

    def new_project(self, name: str, domain: str, uat_name: str, port_prefix: int,
                    url_paths: str, run_command: str, environment_variables: str) -> Optional[ProjectEntity]:
        project = Project(
            name=name, domain=domain, uat_name=uat_name, port_prefix=port_prefix,
            url_paths=url_paths, run_command=run_command, environment_variables=environment_variables)
        self._repo_generator(Project).save(project)
        if project.id:
            return self.entity_adapter.to_project_entity(project)
        else:
            return None

    def get_project(self, id: int) -> Optional[ProjectEntity]:
        project = self._repo_generator(Project).get(id)
        return self.entity_adapter.to_project_entity(project) if project else None

    def get_project_by_name(self, name: str) -> Optional[ProjectEntity]:
        projects = self._repo_generator(Project).get_models_by_query(repo_query=RepoQuery(
            params={'name': name},
        ))
        return self.entity_adapter.to_project_entity(
            projects[0] if projects else None
        )

    def get_boxes(self, project_id: int, offset: int = 0, limit: int = 20) -> List[BoxEntity]:
        boxes = self._repo_generator(Box).get_models_by_query(
            RepoQuery(
                params={'project_id': project_id},
                order_by=[(Box.id, desc)],
                page_params=PageParams(offset=offset, limit=limit)
            )
        )
        return [self.entity_adapter.to_box_entity(box) for box in boxes if box]

    def update_project(
            self,
            id: int,
            **kwargs,
    ):
        if 'name' in kwargs:
            raise errors.UpdatableFieldException(field_name='name')

        self._repo_generator(Project).update(id, **kwargs)
        project = self.get_project(id)
        if project:
            all_boxes = self.get_boxes(project_id=id, limit=1000)
            port_prefix = 0
            for idx, box in enumerate(all_boxes[::-1]):
                if 'port_prefix' in kwargs:
                    if idx == 0:
                        port_prefix = project.port_prefix * 10
                    else:
                        port_prefix += 1
                    self._repo_generator(Box).update(id, port_prefix=port_prefix)
                    box.port_prefix = port_prefix
                for col in ['domain', 'uat_name', 'port_prefix', 'url_paths']:
                    if col in kwargs:
                        gen_nginx_conf(box=box)
                        break
                for col in ['port_prefix', 'run_command', 'environment_variables']:
                    if col in kwargs:
                        gen_supervisor_conf(box=box)
                        break

    def deploy_uat(self, project_id: int, user_id: int, bundle: UploadFile) -> str:
        project = self.get_project(project_id)

        is_admin = self._repo_generator(Admin).exist(user_id=user_id)
        if not is_admin:
            raise errors.AdminOnlyOperationException()

        with tarfile.open(fileobj=bundle.file, mode='r:gz') as tar:
            shutil.rmtree(project.uat_code_dir, ignore_errors=True)
            tar.extractall(project.uat_code_dir)

        output = '\n\n'
        try:
            output += subprocess.check_output(
                [f'{project.uat_venv_dir}/bin/pip', 'install', '-r',
                 f'{project.uat_code_dir}/requirements-dynamic.txt']).decode('utf-8')
        except subprocess.CalledProcessError as e:
            pass

        output += f'supervisor status:\n{"-" * 50}\n'
        supervisor_group = f'{project.uat_app_name}:'
        supervisor_worker_group = f'{project.uat_worker_group}:'
        subprocess.call(['sudo', 'supervisorctl', 'restart', supervisor_group])
        subprocess.call(['sudo', 'supervisorctl', 'restart', supervisor_worker_group])
        try:
            output += subprocess.check_output(['sudo', 'supervisorctl', 'status', supervisor_group]).decode('utf-8')
            output += subprocess.check_output(['sudo', 'supervisorctl', 'status', supervisor_worker_group]).decode('utf-8')
        except subprocess.CalledProcessError as e:
            output += e.output.decode('utf-8')
        output += '\n\n'
        return output

    def alloc_server_port(self, project: ProjectEntity) -> int:
        boxes = self.get_boxes(project_id=project.id, limit=1)
        if boxes:
            port_prefix = boxes[0].port_prefix + 1
        else:
            port_prefix = project.port_prefix * 10

        return port_prefix
