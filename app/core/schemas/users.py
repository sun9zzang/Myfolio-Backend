from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    username: str


class UserInCreate(UserBase):
    password: str


class UserInDB(UserBase):
    user_id: str
    hashed_password: str = ""
    salt: str = ""

    def check_password(self, plain_password: str, hashed_password: str) -> bool:
        ...
        # todo verify_password
