from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.schemas.users import User, UserInCreate
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.dependencies.repositories import get_repository

router = APIRouter()


@router.post(
    "",
    name="auth:register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in_create: UserInCreate = Body(..., embed=True),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    # validate user.email
    try:
        await users_repo.get_user_by_email(user_in_create.email)
    except EntityDoesNotExist:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email is already taken",
        )

    # validate user.username
    try:
        await users_repo.get_user_by_username(user_in_create.username)
    except EntityDoesNotExist:
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username is already taken",
        )

    # validate password
    ...

    user_in_db = await users_repo.create_user(user_in_create)

    return User(
        user_id=user_in_db.user_id,
        email=user_in_db.email,
        username=user_in_db.username,
    )
