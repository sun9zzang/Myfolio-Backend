import bcrypt
from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.mysql import BINARY

from app.core.models.base_generate import Base


class TblUsers(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(320), index=True, nullable=False, unique=True)
    username = Column(String(32), index=True, nullable=False, unique=True)
    salt = Column(BINARY(29), nullable=False)
    hashed_password = Column(BINARY(60), nullable=False)

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode("utf-8"), self.salt)
