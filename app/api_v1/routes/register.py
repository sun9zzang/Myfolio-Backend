from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.schemas.users import User, UserInCreate
from app.db.repositories.users import UsersRepository
from app.dependencies.repositories import get_repository

router = APIRouter()


@router.post(
    "",
    name="auth:register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_in_create: UserInCreate = Body(...),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    # validate user.email
    if users_repo.email_exists(user_in_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email is already taken",
        )

    # validate user.username
    if users_repo.username_exists(user_in_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="username is already taken",
        )

    # validate password
    # todo

    user_in_db = users_repo.create_user(user_in_create)

    return User(
        user_id=user_in_db.user_id,
        email=user_in_db.email,
        username=user_in_db.username,
    )
