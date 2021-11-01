from typing import Callable, Optional

from fastapi import HTTPException, Security, Depends, requests
from fastapi.security import APIKeyHeader
from starlette import status
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import JWT_TOKEN_PREFIX
from app.domain.entities.user import UserEntity, get_user_by_token
from app.domain.services import errors
from app.domain.services.factory import ServiceFactory
from app.domain.services.user import UserService
from app.resources import strings

HEADER_KEY = "Authorization"


class RWAPIKeyHeader(APIKeyHeader):
    async def __call__(  # noqa: WPS610
            self,
            request: requests.Request,
    ) -> Optional[str]:
        try:
            return await super().__call__(request)
        except StarletteHTTPException as original_auth_exc:
            raise HTTPException(
                status_code=original_auth_exc.status_code,
                detail=strings.AUTHENTICATION_REQUIRED,
            )


def get_current_user_authorizer(*, required: bool = True) -> Callable:
    return _get_current_user if required else _get_current_user_optional


def _get_authorization_header_retriever(*, required: bool = True) -> Callable:
    return _get_authorization_header if required else _get_authorization_header_optional


def _get_authorization_header(api_key: str = Security(RWAPIKeyHeader(name=HEADER_KEY))) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.WRONG_TOKEN_PREFIX,
        )

    if token_prefix != JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.WRONG_TOKEN_PREFIX,
        )

    return token


def _get_authorization_header_optional(
        authorization: Optional[str] = Security(
            RWAPIKeyHeader(name=HEADER_KEY, auto_error=False),
        ),
) -> str:
    if authorization:
        return _get_authorization_header(authorization)

    return ""


def _get_current_user(
        token: str = Depends(_get_authorization_header_retriever()),
        user_service: UserService = Depends(ServiceFactory.dependency(UserService))
) -> UserEntity:
    try:
        jwt_user = get_user_by_token(token)
        return user_service.get_user(jwt_user.uid)
    except (ValueError, errors.BoxNotExistException):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.MALFORMED_PAYLOAD,
        )


def _get_current_user_optional(
        token: str = Depends(_get_authorization_header_retriever(required=False)),
        user_service: UserService = Depends(ServiceFactory.dependency(UserService))
) -> Optional[UserEntity]:
    if token:
        return _get_current_user(token, user_service)

    return None
