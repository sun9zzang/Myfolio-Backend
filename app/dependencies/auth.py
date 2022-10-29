from typing import Callable

from fastapi import Depends, Security, HTTPException, status
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.schemas.users import UserInDB
from app.core import strings, jwt
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.dependencies.repositories import get_repository

HEADER_KEY = "Authorization"


def get_current_user_authorizer() -> Callable:
    return _get_current_user


def _get_authorization_header(
    api_key: str = Security(APIKeyHeader(name=HEADER_KEY, auto_error=False)),
) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except (AttributeError, ValueError):
        raise HTTPException(  # todo custom error & error handler
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong token prefix",
        )

    if token_prefix != settings.JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Wrong token prefix",
        )

    return token


def _get_current_user(
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
    token: str = _get_authorization_header(),
) -> UserInDB:
    try:
        user = jwt.get_user_from_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.FORBIDDEN_ERROR,
        )

    try:
        return users_repo.get_user_by_user_id(user.user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.FORBIDDEN_ERROR,
        )
