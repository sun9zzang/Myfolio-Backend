import bcrypt
from typing import Optional

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class User(BaseModel):
    user_id: int
    email: str
    username: str

    def __repr__(self):
        return f"User(user_id={self.user_id!r}, email={self.email!r}, username={self.username!r})"


class UserInCreate(UserBase):
    password: str


class UserInUpdate(User):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None


class UserInLogin(BaseModel):
    email: str
    password: str


class UserWithToken(BaseModel):
    user: User
    token: str


class UserInDB(User):
    salt: bytes
    hashed_password: bytes

    def __repr__(self):
        return (
            f"UserInDB(user_id={self.user_id!r}, email={self.email!r}, username={self.username!r}, "
            f"salt={self.salt!r}, hashed_password={self.hashed_password!r})"
        )

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode("utf-8"), self.salt)

    class Config:
        orm_mode = True
