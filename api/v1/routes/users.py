from fastapi import APIRouter, Body, Depends, Path, status
from fastapi.responses import Response

from app.core import jwt, utils
from app.core.errors.errors import ManagedErrors
from app.core.exceptions import HTTPException
from app.core.openapi import ExampleModelDatas, ResponseSchemaV1
from app.core.schemas.users import (
    User,
    UserInCreate,
    UserInUpdate,
    UserWithToken,
)
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.dependencies.auth import get_current_user_authorizer
from app.dependencies.repositories import get_repository
from app.core.strings import APINames

router = APIRouter()


@router.post(
    "",
    name=APINames.USERS_CREATE_USER_POST,
    status_code=status.HTTP_201_CREATED,
    responses=ResponseSchemaV1.Users.CREATE_USER,
)
async def create_user(
    user_in_create: UserInCreate = Body(..., example=ExampleModelDatas.user_in_create),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    error_list = []

    # validate email
    if not utils.validate_email(user_in_create.email):
        error_list.append(ManagedErrors.invalid_email)
    elif users_repo.email_exists(user_in_create.email):
        error_list.append(ManagedErrors.duplicated_email)

    # validate username
    if not utils.validate_username(user_in_create.username):
        error_list.append(ManagedErrors.duplicated_username)
    elif users_repo.username_exists(user_in_create.username):
        error_list.append(ManagedErrors.duplicated_username)

    # validate password
    if not utils.validate_password(user_in_create.password):
        error_list.append(ManagedErrors.invalid_password)

    if error_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, errors=error_list)

    user_in_db = users_repo.create_user(user_in_create)
    token = jwt.create_access_token_for_user(user_in_db)

    return UserWithToken(
        user=User(**user_in_db.dict(exclude={"salt", "hashed_password"})),
        token=token,
    )


@router.get(
    "/{user_id}",
    name=APINames.USERS_RETRIEVE_USER_GET,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Users.RETRIEVE_USER,
)
async def retrieve_user(
    user_id: int = Path(..., ge=1, example=ExampleModelDatas.user_id),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    try:
        user_in_db = users_repo.get_user_by_user_id(user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            errors=ManagedErrors.not_found,
        )

    return User(**user_in_db.dict())


@router.patch(
    "",
    name=APINames.USERS_UPDATE_USER_PATCH,
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Users.UPDATE_USER,
)
async def update_user(
    user_in_update: UserInUpdate = Body(..., example=ExampleModelDatas.user_in_update),
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    # authorization
    if user_in_update.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=ManagedErrors.forbidden,
        )

    # input data가 모두 None일 시
    if (
        user_in_update.email is None
        and user_in_update.username is None
        and user_in_update.password is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=ManagedErrors.bad_request,
        )

    error_list = []

    # validate email
    if user_in_update.email is not None:
        if not utils.validate_email(user_in_update.email):
            error_list.append(ManagedErrors.invalid_email)
        elif users_repo.email_exists(user_in_update.email):
            error_list.append(ManagedErrors.duplicated_email)

    # validate username
    if user_in_update.username is not None:
        if not utils.validate_username(user_in_update.username):
            error_list.append(ManagedErrors.invalid_username)
        elif users_repo.username_exists(user_in_update.username):
            error_list.append(ManagedErrors.duplicated_username)

    # validate password
    if user_in_update.password is not None:
        if not utils.validate_password(user_in_update.password):
            error_list.append(ManagedErrors.invalid_password)

    if error_list:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=error_list,
        )

    user_in_db = users_repo.update_user(user_in_update)

    return User(**user_in_db.dict())


@router.delete(
    "/{user_id}",
    name=APINames.USERS_DELETE_USER_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ResponseSchemaV1.Users.DELETE_USER,
)
async def delete_user(
    user_id: int = Path(..., ge=1, example=ExampleModelDatas.user_id),
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    # Authorization
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=ManagedErrors.forbidden,
        )

    try:
        users_repo.delete_user(current_user.user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            errors=ManagedErrors.unauthorized,
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
