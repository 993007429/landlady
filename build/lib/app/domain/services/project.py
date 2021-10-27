from typing import Optional

from sqlalchemy import desc

from app.db.models import Box
from app.db.models.project import Project
from app.domain.entities.project import ProjectEntity
from app.domain.services.base import BaseService
from app.infra.repository import RepoQuery, PageParams


class ProjectService(BaseService):

    def new_project(self, name: str, domain: str, uat_name: str, port_prefix: int,
                    url_paths: str, run_command: str) -> Optional[ProjectEntity]:
        project = Project(
            name=name, domain=domain, uat_name=uat_name, port_prefix=port_prefix,
            url_paths=url_paths, run_command=run_command)
        self._repo_generator(Project).save(project)
        if project.id:
            return self.entity_adapter.to_project_entity(project)
        else:
            return None

    def get_project_by_name(self, name: str) -> Optional[ProjectEntity]:
        projects = self._repo_generator(Project).get_models_by_query(repo_query=RepoQuery(
            params={'name': name},
        ))
        return self.entity_adapter.to_project_entity(
            projects[0] if projects else None
        )

    def alloc_server_port(self, project: ProjectEntity) -> int:
        boxes = self._repo_generator(Box).get_models_by_query(repo_query=RepoQuery(
            params={'project_id': project.id},
            order_by=[(Box.port_prefix, desc)],
            page_params=PageParams(offset=0, limit=1)
        ))
        if boxes:
            port_prefix = boxes[0].port_prefix + 1
        else:
            port_prefix = int(project.port_prefix) * 10

        return port_prefix
