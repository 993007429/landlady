from typing import Optional

from app.db.models.box import Box
from app.db.models.project import Project
from app.db.models.user import User
from app.domain.entities.box import BoxEntity
from app.domain.entities.project import ProjectEntity
from app.domain.entities.user import UserEntity
from app.infra.repository import RepoGenerator


class EntityAdapter:
    def __init__(self, repo_generator: RepoGenerator):
        self._repo_generator = repo_generator

    def to_box_entity(self, box: Box) -> BoxEntity:
        repos = self._repo_generator
        entity = BoxEntity(id=box.id)
        entity.project = self.to_project_entity(repos(Project).get(box.project_id))
        entity.user = self.to_user_entity(repos(User).get(box.user_id))
        entity.port_prefix = box.port_prefix
        entity.numprocs = box.numprocs
        entity.start_time = box.start_time
        entity.status = box.status
        return entity

    def to_user_entity(self, user: User) -> Optional[UserEntity]:
        if not user:
            return
        entity = UserEntity(id=user.id, name=user.name)
        return entity

    def to_project_entity(self, project: Project) -> Optional[ProjectEntity]:
        if not project:
            return None
        entity = ProjectEntity(
            id=project.id, name=project.name, domain=project.domain, uat_name=project.uat_name,
            port_prefix=project.port_prefix, url_paths=project.url_paths.split(','), run_command=project.run_command)

        return entity
