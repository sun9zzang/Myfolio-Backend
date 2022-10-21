from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class User(UserBase):
    user_id: int


class UserInCreate(UserBase):
    password: str


class UserInUpdate(User):
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


class UserInDB(User):
    salt: bytes
    hashed_password: bytes

    class Config:
        orm_mode = True
