from datetime import datetime, timedelta

import jwt
from pydantic import ValidationError

from app.core.config import settings
from app.core.schemas.jwt import JWTUser, JWTMetadata
from app.core.schemas.users import UserInDB


def create_jwt_token(
    *,
    jwt_content: dict,
    secret_key: str,
    expires_delta: timedelta,
) -> str:
    to_encode = jwt_content.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update(JWTMetadata(exp=expire, sub=settings.JWT_SUBJECT).dict())
    return jwt.encode(to_encode, secret_key, algorithm=settings.ALGORITHM)


def create_access_token_for_user(
    user_in_db: UserInDB,
) -> str:
    return create_jwt_token(
        jwt_content=JWTUser(
            user_id=user_in_db.user_id,
            email=user_in_db.email,
            username=user_in_db.username,
        ).dict(),
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def get_user_id_from_token(token: str) -> int:
    try:
        return JWTUser(
            **jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        ).user_id
    except jwt.PyJWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error
