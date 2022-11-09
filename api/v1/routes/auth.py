from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.schemas.users import User, UserInLogin, UserInDB
from app.core import strings, jwt
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.dependencies.repositories import get_repository
from app.dependencies.auth import get_current_user_authorizer


router = APIRouter()


@router.post(
    "/login",
    name="auth:login",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "user와 token을 반환합니다.",
        },
        status.HTTP_400_BAD_REQUEST: {
            "content": {"application/json": {}},
            "description": "로그인에 실패 시 에러를 반환합니다.",
        },
    },
)
async def login(
    user_in_login: UserInLogin = Body(...),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    login_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.WRONG_CREDENTIALS_ERROR,
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
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "인증 성공 시 user를 반환합니다.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "content": {"application/json": {}},
            "description": "인증 정보가 없을 경우 에러를 반환합니다.",
        },
        status.HTTP_403_FORBIDDEN: {
            "content": {"application/json": {}},
            "description": "인증 정보가 잘못된 경우 에러를 반환합니다.",
        },
    },
)
async def get_user_from_token(
    current_user: UserInDB = Depends(get_current_user_authorizer()),
):
    return User(**current_user.dict(exclude={"salt", "hashed_password"}))


@router.get(
    "/renew-token",
    name="auth:renew_token",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "content": {"application/json": {}},
            "description": "인증 성공 시 새로 발급된 token을 반환합니다.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "content": {"application/json": {}},
            "description": "인증 정보가 없을 경우 에러를 반환합니다.",
        },
        status.HTTP_403_FORBIDDEN: {
            "content": {"application/json": {}},
            "description": "인증 정보가 잘못된 경우 에러를 반환합니다.",
        },
    },
)
async def renew_token(
    current_user: UserInDB = Depends(get_current_user_authorizer()),
):
    token = jwt.create_access_token_for_user(current_user)

    return {"token": token}
