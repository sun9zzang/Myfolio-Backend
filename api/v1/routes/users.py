from fastapi import APIRouter, Body, Depends, status
from fastapi.responses import Response
# from fastapi.exceptions import HTTPException

from app.core.schemas.users import User, UserInCreate, UserInUpdate, UserWithToken
from app.core.schemas.errors import Error, ErrorList
from app.core.schemas.responses import ResponseSchemaV1
from app.core.exceptions import HTTPException
from app.core.strings import ErrorStrings
from app.core import jwt, utils
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.dependencies.auth import get_current_user_authorizer
from app.dependencies.repositories import get_repository


router = APIRouter()


@router.post(
    "",
    name="users:create_user",
    status_code=status.HTTP_201_CREATED,
    responses=ResponseSchemaV1.Users.CREATE_USER,
)
async def create_user(
    user_in_create: UserInCreate = Body(...),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    error_list = ErrorList()

    # validate email
    if not utils.validate_email(user_in_create.email):
        error_list.append(
            Error(
                message=ErrorStrings.invalid_email.value,
                code=ErrorStrings.invalid_email.name,
            )
        )
    elif users_repo.email_exists(user_in_create.email):
        error_list.append(
            Error(
                message=ErrorStrings.duplicated_email.value,
                code=ErrorStrings.duplicated_email.name,
            )
        )

    # validate username
    if not utils.validate_username(user_in_create.username):
        error_list.append(
            Error(
                message=ErrorStrings.invalid_username.value,
                code=ErrorStrings.invalid_username.name,
            )
        )
    elif users_repo.username_exists(user_in_create.username):
        error_list.append(
            Error(
                message=ErrorStrings.duplicated_username.value,
                code=ErrorStrings.duplicated_username.name,
            )
        )

    # validate password
    if not utils.validate_password(user_in_create.password):
        error_list.append(
            Error(
                message=ErrorStrings.invalid_password.value,
                code=ErrorStrings.invalid_password.name,
            )
        )

    if error_list.errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, errors=error_list
        )

    user_in_db = users_repo.create_user(user_in_create)
    token = jwt.create_access_token_for_user(user_in_db)

    return UserWithToken(
        user=User(**user_in_db.dict(exclude={"salt", "hashed_password"})),
        token=token,
    )


@router.get(
    "/{user_id}",
    name="users:retrieve_user",
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Users.RETRIEVE_USER,
)
async def retrieve_user(
    user_id: int,
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    error_list = ErrorList()

    try:
        user_in_db = users_repo.get_user_by_user_id(user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=error_list.append(
                Error(
                    message=ErrorStrings.user_not_found.value,
                    code=ErrorStrings.user_not_found.name,
                ),
            ),
        )

    return User(**user_in_db.dict(exclude={"salt", "hashed_password"}))


@router.patch(
    "",
    name="users:update_user",
    status_code=status.HTTP_200_OK,
    responses=ResponseSchemaV1.Users.UPDATE_USER,
)
async def update_user(
    user_in_update: UserInUpdate = Body(...),
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    error_list = ErrorList()

    # authorization
    if user_in_update.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=error_list.append(
                Error(
                    message=ErrorStrings.forbidden.value,
                    code=ErrorStrings.forbidden.name,
                ),
            ),
        )

    # input data가 모두 None일 시
    if (
        user_in_update.email is None
        and user_in_update.username is None
        and user_in_update.password is None
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=error_list.append(
                Error(
                    message=ErrorStrings.bad_request.value,
                    code=ErrorStrings.bad_request.name,
                ),
            ),
        )

    # validate email
    if user_in_update.email is not None:
        if not utils.validate_email(user_in_update.email):
            error_list.append(Error(
                message=ErrorStrings.invalid_email.value,
                code=ErrorStrings.invalid_email.name,
            ))
        elif users_repo.email_exists(user_in_update.email):
            error_list.append(Error(
                message=ErrorStrings.duplicated_email.value,
                code=ErrorStrings.duplicated_email.name,
            ))

    # validate username
    if user_in_update.username is not None:
        if not utils.validate_username(user_in_update.username):
            error_list.append(Error(
                message=ErrorStrings.invalid_username.value,
                code=ErrorStrings.invalid_username.name,
            ))
        if users_repo.username_exists(user_in_update.username):
            error_list.append(Error(
                message=ErrorStrings.duplicated_username.value,
                code=ErrorStrings.duplicated_username.name,
            ))

    # validate password
    if user_in_update.password is not None:
        if not utils.validate_password(user_in_update.password):
            error_list.append(Error(
                message=ErrorStrings.invalid_password.value,
                code=ErrorStrings.invalid_password.name,
            ))

    if error_list.errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=error_list,
        )

    user_in_db = users_repo.update_user(user_in_update)

    return User(**user_in_db.dict())


@router.delete(
    "/{user_id}",
    name="users:delete_user",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ResponseSchemaV1.Users.DELETE_USER,
)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user_authorizer()),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    error_list = ErrorList()

    # Authorization
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            errors=error_list.append(
                Error(
                    message=ErrorStrings.forbidden.value,
                    code=ErrorStrings.forbidden.name,
                ),
            ),
        )

    try:
        users_repo.delete_user(current_user.user_id)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            errors=error_list.append(
                Error(
                    message=ErrorStrings.user_not_found.value,
                    cone=ErrorStrings.user_not_found.name,
                )
            ),
        )
    else:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
