from typing import Optional

import bcrypt
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class User(BaseModel):
    user_id: int
    email: str
    username: str


class UserInCreate(UserBase):
    password: str


class UserInUpdate(User):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserInLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    token: str


class UserWithToken(BaseModel):
    user: User
    token: str


class UserInDB(User):
    salt: bytes
    hashed_password: bytes

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode("utf-8"), self.salt)

    class Config:
        orm_mode = True
