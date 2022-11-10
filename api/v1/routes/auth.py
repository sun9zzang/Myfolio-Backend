from fastapi import APIRouter, Body, Depends, status

from app.core.schemas.errors import Error, ErrorList
from app.core.schemas.users import User, UserInLogin, UserInDB
from app.core.schemas.responses import ResponseSchemaV1
from app.core.exceptions import HTTPException
from app.core.strings import ErrorStrings
from app.core import jwt
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.dependencies.repositories import get_repository
from app.dependencies.auth import get_current_user_authorizer


router = APIRouter()


@router.post(
    "/login",
    name="auth:login",
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Auth.LOGIN,
)
async def login(
    user_in_login: UserInLogin = Body(...),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    error_list = ErrorList()

    login_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        errors=error_list.append(
            Error(
                message=ErrorStrings.invalid_credentials.value,
                code=ErrorStrings.invalid_credentials.name,
            )
        ),
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
    user = User(**user_in_db.dict(exclude={"salt", "hashed_password"}))

    return {
        "user": user.dict(),
        "token": token,
    }


@router.get(
    "/user-retriever",
    name="auth:retrieve_user_from_token",
    response_model=User,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Auth.USER_RETRIEVER,
)
async def get_user_from_token(
    current_user: UserInDB = Depends(get_current_user_authorizer()),
):
    return User(**current_user.dict(exclude={"salt", "hashed_password"}))


@router.get(
    "/renew-token",
    name="auth:renew_token",
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Auth.RENEW_TOKEN,
)
async def renew_token(
    current_user: UserInDB = Depends(get_current_user_authorizer()),
):
    token = jwt.create_access_token_for_user(current_user)

    return {"token": token}
