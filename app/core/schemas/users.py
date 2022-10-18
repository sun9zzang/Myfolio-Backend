from pydantic import BaseModel

from app.core import security


class UserBase(BaseModel):
    email: str
    username: str


class User(UserBase):
    user_id: int


class UserInCreate(UserBase):
    password: str


class UserInUpdate(UserBase):
    user_id: int
    email: str | None = None
    username: str | None = None
    password: str | None = None


class UserInLogin(BaseModel):
    email: str
    password: str


class UserWithToken(User):
    token: str


class UserInResponse(BaseModel):
    user: UserWithToken


class UserInDB(UserBase):
    user_id: int | None = None
    hashed_password: bytes = b""
    salt: bytes = b""

    def check_password(self, password: str) -> bool:
        return security.verify_password(password, self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.hashed_password = security.get_password_hash(password, self.salt)

    class Config:
        orm_mode: True
