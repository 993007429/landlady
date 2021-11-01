from typing import Optional

from sqlalchemy.exc import SQLAlchemyError

from app.db.models.user import User
from app.domain.entities.user import UserEntity
from app.domain.services.base import BaseService
from app.domain.services.errors import NewEntityFailException


class UserService(BaseService):

    def new_user(self, name: str):
        try:
            user = User(
                name=name,
            )
            self._repo_generator(User).save(user)
            return self.entity_adapter.to_user_entity(user)
        except SQLAlchemyError as e:
            raise NewEntityFailException() from e

    def get_user(self, user_id: int) -> Optional[UserEntity]:
        user = self._repo_generator(User).get(user_id)
        if not user:
            return None
        return self.entity_adapter.to_user_entity(user)
