import datetime
from typing import Optional

import jwt
from pydantic import ValidationError

from app.api.schemas.jwt import JWTUser
from app.config import LOGIN_TOKEN_SECRET
from app.domain.entities.rwmodel import RWModel


class UserEntity(RWModel):
    id: int
    name: str

    def gen_login_token(self, expire_days: int = 30) -> str:
        """生成jwt token，payload中携带用户基础信息"""
        payload = dict(
            exp=datetime.datetime.utcnow() + datetime.timedelta(days=expire_days),
            uid=self.id,
            name=self.name,
        )
        return jwt.encode(payload, LOGIN_TOKEN_SECRET)


def get_user_by_token(token: str) -> Optional[JWTUser]:
    """解析jwt token中携带的用户基础信息"""
    payload = jwt.decode(token, LOGIN_TOKEN_SECRET, algorithms='HS256')
    if not payload:
        return None
    try:
        return JWTUser(uid=payload['uid'], name=payload['name'])
    except (jwt.PyJWTError, ValidationError):
        pass
