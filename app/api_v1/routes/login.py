from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.schemas.users import UserInLogin, UserWithToken, UserInResponse
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.dependencies.repositories import get_repository
from app.core import jwt


router = APIRouter()


@router.post(
    "",
    name="auth:login",
    response_model=UserInResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    user_in_login: UserInLogin = Body(...),
    users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
):
    login_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Wrong email or password",
    )

    try:
        user_in_db = users_repo.validate_login(user_in_login)
    except EntityDoesNotExist:
        raise login_error
    else:
        token = jwt.create_access_token_for_user(user_in_db)
        return UserInResponse(
            user=UserWithToken(
                user_id=user_in_db.user_id,
                email=user_in_db.email,
                username=user_in_db.username,
                token=token,
            )
        )
