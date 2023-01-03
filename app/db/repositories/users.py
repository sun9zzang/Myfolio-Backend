from typing import Optional

from sqlalchemy import select

from app.core.models.users import TblUsers
from app.core.schemas.users import UserInCreate, UserInDB, UserInUpdate
from app.db.errors import EntityDoesNotExist
from app.db.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    def get_user_by_user_id(self, user_id: int) -> UserInDB:
        with self.get_session() as session:
            user = session.get(TblUsers, user_id)

            if user is not None:
                return UserInDB.from_orm(user)
            else:
                raise EntityDoesNotExist

    def _get_user_model_by_email(self, email: str) -> Optional[TblUsers]:
        with self.get_session() as session:
            query = select(TblUsers).where(TblUsers.email == email)
            user = session.scalars(query).first()

            return user

    def email_exists(self, email: str) -> bool:
        subquery = select(TblUsers).where(TblUsers.email == email).exists()
        query = select(subquery)

        with self.get_session() as session:
            if session.scalars(query).first():
                return True
            else:
                return False

    def get_user_by_email(self, email: str) -> UserInDB:
        user = self._get_user_model_by_email(email)

        if user is not None:
            return UserInDB.from_orm(user)
        else:
            raise EntityDoesNotExist

    def username_exists(self, username: str) -> bool:
        subquery = (
            select(TblUsers).where(TblUsers.username == username).exists()
        )
        query = select(subquery)

        with self.get_session() as session:
            if session.scalars(query).first():
                return True
            else:
                return False

    def _get_user_model_by_username(self, username: str) -> Optional[TblUsers]:
        with self.get_session() as session:
            query = select(TblUsers).where(TblUsers.username == username)
            user = session.scalars(query).first()

            return user

    def get_user_by_username(self, username: str) -> UserInDB:
        user = self._get_user_model_by_username(username)

        if user is not None:
            return UserInDB.from_orm(user)
        else:
            raise EntityDoesNotExist

    def create_user(self, user_in_create: UserInCreate) -> UserInDB:
        user = TblUsers(
            email=user_in_create.email,
            username=user_in_create.username,
        )
        user.change_password(user_in_create.password)

        with self.get_session() as session:
            session.add(user)
            session.commit()

            return UserInDB.from_orm(user)

    def update_user(self, user_in_update: UserInUpdate) -> UserInDB:
        with self.get_session() as session:
            user = session.get(TblUsers, user_in_update.id)

            user.email = user_in_update.email or user.email
            user.username = user_in_update.username or user.username
            if user_in_update.password:
                user.change_password(user_in_update.password)

            session.commit()

            return UserInDB.from_orm(user)

    def delete_user(self, user_id: int) -> None:
        with self.get_session() as session:
            user = session.get(TblUsers, user_id)

            if user is not None:
                session.delete(user)
                session.commit()
            else:
                raise EntityDoesNotExist
