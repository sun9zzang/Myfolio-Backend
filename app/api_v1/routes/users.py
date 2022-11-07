from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import Response
from fastapi.exceptions import HTTPException

from app.core.schemas.users import User, UserInCreate, UserInUpdate
from app.core.config import settings
from app.core import strings, utils
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
    validation_flags = {
        "email": False,
        "username": False,
        "password": False,
    }
    # validate email
    if utils.validate_email(user_in_create.email):
        validation_flags["email"] = True

    # validate username
    if utils.validate_username(user_in_create.username):
        validation_flags["username"] = True

    if utils.validate_password(user_in_create.password):
        validation_flags["password"] = True

    invalid_field_str = []
    for key, value in validation_flags.items():
        if not value:
            invalid_field_str.append(key)
    if invalid_field_str:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"유효한 {', '.join(invalid_field_str)}이(가) 아닙니다."
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

    return User(**user_in_db.dict(exclude={"salt", "hashed_password"}))


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

    validation_flags = {}
    for key in user_in_update.dict(exclude={"user_id"}, exclude_none=True).keys():
        validation_flags.update({key: {"is_valid": False, "is_unique": False}})

    # input data가 모두 None일 시
    if user_in_update.email is None and user_in_update.username is None and user_in_update.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.HTTP_400_BAD_REQUEST,
        )

    # validate email
    if user_in_update.email is not None:
        if utils.validate_email(user_in_update.email):
            validation_flags["email"]["is_valid"] = True
        if not users_repo.email_exists(user_in_update.email):
            validation_flags["email"]["is_unique"] = True

    # validate username
    if user_in_update.username is not None:
        if utils.validate_username(user_in_update.username):
            validation_flags["username"]["is_valid"] = True
        if not users_repo.username_exists(user_in_update.username):
            validation_flags["username"]["is_unique"] = True

    # validate password
    if user_in_update.password is not None:
        validation_flags["password"]["is_unique"] = True
        if utils.validate_password(user_in_update.password):
            validation_flags["password"]["is_valid"] = True

    invalid_field_str = []
    duplicated_field_str = []
    error_detail = ""

    for key, value in validation_flags.items():
        if not value["is_valid"]:
            invalid_field_str.append(key)
        if not value["is_unique"]:
            duplicated_field_str.append(key)

    if invalid_field_str:
        if duplicated_field_str:
            error_detail = (
                f"유효한 {', '.join(invalid_field_str)}이(가) 아닙니다. "
                f"또한 {', '.join(duplicated_field_str)}이(가) 이미 존재합니다."
            )
        else:
            error_detail = f"유효한 {', '.join(invalid_field_str)}이(가) 아닙니다."
    elif duplicated_field_str:
        error_detail = f"{', '.join(duplicated_field_str)}이(가) 이미 존재합니다."

    if error_detail:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_detail,
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
