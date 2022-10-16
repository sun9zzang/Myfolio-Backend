from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.models.users import TblUsers
from app.core.schemas.users import UserInDB, UserInCreate
from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist, EntityAlreadyExists


class UsersRepository(BaseRepository):

    async def get_user_by_user_id(self, user_id: int) -> UserInDB:
        with self.get_session() as session:
            user: TblUsers = session.get(TblUsers, {"user_id": user_id})

            return user.convert_to_schema()

    async def get_user_by_email(self, email: str) -> UserInDB:
        with self.get_session() as session:
            user: TblUsers = session.get(TblUsers, {"email": email})

            return user.convert_to_schema()

    async def create_user(self, user_in_create: UserInCreate) -> UserInDB:

