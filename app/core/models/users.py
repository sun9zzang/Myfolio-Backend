import bcrypt
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import BINARY, INTEGER

from app.core.models.base_generate import Base
from app.core.config import settings


class TblUsers(Base):
    __tablename__ = "users"

    user_id = Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True)
    email = Column(
        String(settings.EMAIL_MAX_LENGTH), index=True, nullable=False, unique=True
    )
    username = Column(
        String(settings.USERNAME_MAX_LENGTH), index=True, nullable=False, unique=True
    )
    salt = Column(BINARY(29), nullable=False)
    hashed_password = Column(BINARY(60), nullable=False)

    templates = relationship("TblTemplates", back_populates="user")

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), self.hashed_password)

    def change_password(self, password: str) -> None:
        self.salt = bcrypt.gensalt()
        self.hashed_password = bcrypt.hashpw(password.encode("utf-8"), self.salt)
