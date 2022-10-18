from sqlalchemy import Column, String, Integer, LargeBinary

from app.core.models.base import Base


class TblUsers(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, primary_key=True)
    username = Column(String, index=True, nullable=False)
    hashed_password = Column(LargeBinary)
    salt = Column(LargeBinary)
