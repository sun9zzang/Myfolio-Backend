from fastapi import APIRouter, Body, Depends, status

from app.core import jwt
from app.core.errors.errors import ManagedErrors
from app.core.exceptions import HTTPException
from app.core.openapi import ExampleModelDatas, ResponseSchemaV1
from app.core.schemas.users import (
    Token,
    User,
    UserInDB,
    UserInLogin,
    UserWithToken,
)
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.dependencies.auth import get_current_user_authorizer
from app.dependencies.repositories import get_repository
from app.core.strings import APINames

router = APIRouter()


@router.post(
    "/login",
    name=APINames.AUTH_LOGIN_POST,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Auth.LOGIN,
)
async def login(
    user_in_login: UserInLogin = Body(..., example=ExampleModelDatas.user_in_login),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    login_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        errors=ManagedErrors.invalid_credentials,
    )

    # validate email
    try:
        user_in_db = users_repo.get_user_by_email(user_in_login.email)
    except EntityDoesNotExist:
        raise login_error

    # validate password
    if not user_in_db.check_password(user_in_login.password):
        raise login_error

    token = jwt.create_access_token_for_user(user_in_db)
    user = User(**user_in_db.dict())

    return UserWithToken(
        user=user,
        token=token,
    )


@router.get(
    "/user-retriever",
    name=APINames.AUTH_USER_RETRIEVER_GET,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Auth.USER_RETRIEVER,
)
async def get_user_from_token(
    current_user: UserInDB = Depends(get_current_user_authorizer()),
):
    return User(**current_user.dict(exclude={"salt", "hashed_password"}))


@router.get(
    "/renew-token",
    name=APINames.AUTH_RENEW_TOKEN_GET,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Auth.RENEW_TOKEN,
)
async def renew_token(
    current_user: UserInDB = Depends(get_current_user_authorizer()),
):
    return Token(token=jwt.create_access_token_for_user(current_user))
