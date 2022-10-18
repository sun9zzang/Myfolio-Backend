from sqlalchemy import select

from app.core.models.users import TblUsers
from app.core.schemas.users import UserInDB, UserInCreate, UserInUpdate
from app.core import security
from app.db.repositories.base import BaseRepository
from app.db.errors import EntityDoesNotExist


class UsersRepository(BaseRepository):
    async def get_user_by_user_id(self, user_id: int) -> UserInDB:
        with self.get_session() as session:
            user = session.get(TblUsers, {"user_id": user_id})

            if user is not None:
                return UserInDB.from_orm(user)
            else:
                raise EntityDoesNotExist

    async def get_user_by_email(self, email: str) -> UserInDB:
        with self.get_session() as session:
            user = session.get(TblUsers, {"email": email})

            if user is not None:
                return UserInDB.from_orm(user)
            else:
                raise EntityDoesNotExist

    async def get_user_by_username(self, username: str) -> UserInDB:
        with self.get_session() as session:
            query = select(TblUsers).filter_by(username=username)
            user = session.scalars(query).first()

            if user is not None:
                return UserInDB.from_orm(user)
            else:
                raise EntityDoesNotExist

    async def create_user(self, user_in_create: UserInCreate) -> UserInDB:
        user_in_db = UserInDB(
            email=user_in_create.email,
            username=user_in_create.username,
        )
        user_in_db.change_password(user_in_create.password)

        with self.get_session() as session:
            user_tbl = TblUsers(**user_in_db.dict(exclude={"user_id"}))
            session.add(user_tbl)
            user_in_db.user_id = user_tbl.user_id

        return user_in_db

    async def update_user(self, user_in_update: UserInUpdate) -> UserInDB:
        with self.get_session() as session:
            user_tbl = session.get(TblUsers, {"user_id": user_in_update.user_id})
            user_tbl.email = user_in_update.email or user_tbl.email
            user_tbl.username = user_in_update.username or user_tbl.username

            if user_in_update.password:
                user_tbl.salt = security.generate_salt()
                user_tbl.hashed_password = security.get_password_hash(
                    user_in_update.password, user_tbl.salt
                )

            return UserInDB.from_orm(user_tbl)

    async def withdraw_user(self, user_id: int) -> None:
        with self.get_session() as session:
            user_tbl = session.get(TblUsers, {"user_id": user_id})
            session.delete(user_tbl)
