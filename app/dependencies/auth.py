from typing import Callable, Optional

from fastapi import Depends, Security, status
from fastapi.security import APIKeyHeader

from app.core import jwt
from app.core.config import settings
from app.core.errors.errors import ManagedErrors
from app.core.exceptions import HTTPException
from app.core.schemas.users import UserInDB
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.dependencies.repositories import get_repository

AUTHORIZATION_HEADER_KEY = "Authorization"


def get_current_user_authorizer() -> Callable[[], UserInDB]:
    return get_current_user


def _get_authorization_header(
    api_key: Optional[str] = Security(
        APIKeyHeader(name=AUTHORIZATION_HEADER_KEY, auto_error=False)
    ),
) -> str:
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=ManagedErrors.unauthorized,
        )

    try:
        token_prefix, token = api_key.split(" ")
    except (AttributeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=ManagedErrors.unauthorized,
        )

    if token_prefix != settings.JWT_TOKEN_PREFIX:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=ManagedErrors.unauthorized,
        )

    return token


def _get_authorization_header_retriever() -> Callable[[], str]:
    return _get_authorization_header


def get_current_user(
    token: str = Depends(_get_authorization_header_retriever()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserInDB:
    try:
        user = jwt.get_user_from_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=ManagedErrors.unauthorized,
        )

    try:
        return users_repo.get_user_by_user_id(user.user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=ManagedErrors.unauthorized,
        )
