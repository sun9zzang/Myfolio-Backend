from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class User(UserBase):
    user_id: int

    def __repr__(self):
        return f"User(user_id={self.user_id!r}, email={self.email!r}, username={self.username!r})"


class UserInCreate(UserBase):
    password: str


class UserInUpdate(User):
    email: str | None = None
    username: str | None = None
    password: str | None = None


class UserInLogin(BaseModel):
    email: str
    password: str


class UserInDB(User):
    salt: bytes
    hashed_password: bytes

    def __repr__(self):
        return (
            f"UserInDB(user_id={self.user_id!r}, email={self.email!r}, username={self.username!r}, "
            f"salt={self.salt!r}, hashed_password={self.hashed_password!r})"
        )

    class Config:
        orm_mode = True
