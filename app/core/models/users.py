from sqlalchemy import Column, String, Integer

from app.core.models.base import Base
from app.core.schemas.users import UserInDB


class TblUsers(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, primary_key=True)
    username = Column(String, index=True, nullable=False)
    hashed_password = Column(String)
    salt = Column(String)

    def convert_to_schema(self) -> UserInDB:
        # convert to app.core.schemas.users.UserInDB schema

        return UserInDB(
            user_id=self.user_id,
            email=self.email,
            username=self.username,
            hashed_password=self.hashed_password,
            salt=self.salt,
        )
