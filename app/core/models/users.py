from sqlalchemy import Column, String

from app.core.models.base import Base


class TblUsers(Base):
    __tablename__ = "user"

    user_id = Column(String, primary_key=True)
    email = Column(String, primary_key=True)
    username = Column(String, primary_key=True)
    hashed_password = Column(String)
    salt = Column(String)
