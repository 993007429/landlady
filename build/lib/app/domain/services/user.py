from typing import Optional

from app.db.models.user import User
from app.domain.entities.user import UserEntity
from app.domain.services.base import BaseService


class UserService(BaseService):

    def get_user(self, user_id: int) -> Optional[UserEntity]:
        user = self._repo_generator(User).get(user_id)
        if not user:
            return None
        return self.entity_adapter.to_user_entity(user)
