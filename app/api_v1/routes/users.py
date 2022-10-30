import re

from fastapi import APIRouter, Body, Depends, Response, HTTPException, status

from app.core.schemas.users import User, UserInCreate, UserInUpdate
from app.core.config import settings
from app.core import strings
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.dependencies.auth import get_current_user_authorizer
from app.dependencies.repositories import get_repository


router = APIRouter()


@router.post(
    "",
    name="users:create_user",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    user_in_create: UserInCreate = Body(...),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    # validate email
    if (
        len(user_in_create.email) > settings.EMAIL_MAX_LENGTH
        or re.compile(settings.EMAIL_REGEX).match(user_in_create.email) is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효한 이메일이 아닙니다.",
        )

    # todo validate username
    if not 2 <= len(user_in_create.username) <= 16:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효한 유저 이름이 아닙니다.",
        )

    # todo validate password
    if not 8 <= len(user_in_create.password) <= 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효한 비밀번호가 아닙니다.",
        )

    user_in_db = users_repo.create_user(user_in_create)

    return User(**user_in_db.dict())


@router.get(
    "/{user_id}",
    name="users:retrieve_user",
    response_model=User,
    status_code=status.HTTP_200_OK,
)
async def retrieve_user(
    user_id: int,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    try:
        user_in_db = users_repo.get_user_by_user_id(user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효한 user_id가 아닙니다.",
        )

    return User(**user_in_db.dict())


@router.patch(
    "",
    name="users:update_user",
    response_model=User,
    status_code=status.HTTP_200_OK,
)
async def update_user(
    user_in_update: UserInUpdate = Body(...),
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    # authorization
    if user_in_update.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.HTTP_403_FORBIDDEN_ERROR,
        )

    # validate email
    if user_in_update.email is not None:
        if (
            len(user_in_update.email) > settings.EMAIL_MAX_LENGTH
            or re.compile(settings.EMAIL_REGEX).match(user_in_update.email) is None
        ):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="유효한 이메일이 아닙니다.")
        elif users_repo.email_exists(user_in_update.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="중복된 이메일입니다.",
            )

    if user_in_update.username is not None:
        if 2 <= len(user_in_update.username) <= 16:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효한 유저 이름이 아닙니다.",
            )
        elif users_repo.username_exists(user_in_update.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="중복된 유저 이름입니다.",
            )

    if user_in_update.password is not None:
        if 8 <= len(user_in_update.password) <= 50:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="유효한 패스워드가 아닙니다.",
            )

    user_in_db = users_repo.update_user(user_in_update)

    return User(**user_in_db.dict())


@router.delete(
    "/{user_id}",
    name="users:delete_user",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    # authorization
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.HTTP_403_FORBIDDEN_ERROR,
        )

    try:
        users_repo.delete_user(user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효한 user_id가 아닙니다.",
        )
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
