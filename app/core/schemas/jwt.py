from datetime import datetime

from pydantic import BaseModel


class JWTUser(BaseModel):
    user_id: int
    email: str
    username: str


class JWTMetadata(BaseModel):
    exp: datetime
    sub: str
