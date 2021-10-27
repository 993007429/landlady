from typing import TypeVar

from app.domain.entities.box import BoxEntity
from app.domain.entities.project import ProjectEntity
from app.domain.entities.user import UserEntity
from app.domain.services.box import BoxService
from app.domain.services.project import ProjectService
from app.domain.services.user import UserService

S = TypeVar('S', BoxService, UserService, ProjectService)
E = TypeVar('E', BoxEntity, UserEntity, ProjectEntity)
