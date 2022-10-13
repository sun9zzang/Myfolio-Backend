from uuid import uuid4

from sqlalchemy.orm import Session

from app.core.models.users import TblUsers
from app.core.schemas.users import UserInDB, UserInCreate
from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist, EntityAlreadyExists


class UsersRepository(BaseRepository):

    async def get_user_by_id(self, user_id: str) -> UserInDB:
        with self.get_session() as session:
            session: Session

            user_row = session.query(TblUsers).filter(TblUsers.user_id == user_id).first()
            if user_row is not None:
                return UserInDB(user_row.__dict__)
        raise EntityDoesNotExist(
            f"User with user_id({user_id}) does not exists"
        )

    async def get_user_by_email(self, email: str) -> UserInDB:
        with self.get_session() as session:
            session: Session

            user_row = session.query(TblUsers).filter(TblUsers.email == email).first()
            if user_row is not None:
                return UserInDB(user_row.__dict__)
        raise EntityDoesNotExist(
            f"User with email({email}) does not exists"
        )

    async def get_user_by_username(self, username: str) -> UserInDB:
        with self.get_session() as session:
            session: Session

            user_row = session.query(TblUsers).filter(TblUsers.username == username).first()
            if user_row is not None:
                return UserInDB(user_row.__dict__)
        raise EntityDoesNotExist(
            f"User with username({username}) does not exists"
        )

    async def _is_email_taken(self, email: str) -> bool:
        with self.get_session() as session:
            session: Session

            user_row = session.query(TblUsers).filter(TblUsers.email == email).first()
            if user_row is None:
                return True
            return False

    async def _is_username_taken(self, username: str) -> bool:
        with self.get_session() as session:
            session: Session

            user_row = session.query(TblUsers).filter(TblUsers.username == username).first()
            if user_row is None:
                return True
            return False

    async def create_user(self, user_in_create: UserInCreate) -> UserInDB:
        with self.get_session() as session:
            session: Session

            if await self._is_email_taken(user_in_create.email):
                raise EntityAlreadyExists(
                    f"email({user_in_create.email}) already taken"
                )

            if await self._is_username_taken(user_in_create.username):
                raise EntityAlreadyExists(
                    f"username({user_in_create.username}) already taken"
                )

            user_in_db = UserInDB(
                user_id=str(uuid4()),
                email=user_in_create.email,
                username=user_in_create.username,
            )




