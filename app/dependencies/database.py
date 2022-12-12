from contextlib import AbstractContextManager, contextmanager

from fastapi import status
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from pymysql.err import OperationalError

from app.core.config import config
from app.core.errors.errors import ManagedErrors
from app.core.models import base
from app.core.exceptions import HTTPException


class DB:
    def __init__(self, dsn: str, **options) -> None:
        try:
            self._engine = create_engine(dsn, **options)
        except OperationalError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors=ManagedErrors.internal_server_error,
            )
        self._make_session = sessionmaker(bind=self._engine)
        self._Base = base.Base
        self._Base.metadata.create_all(bind=self._engine)

    @contextmanager
    def get_session(self) -> AbstractContextManager[Session]:
        session = self._make_session()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = DB(config.MYSQL_DSN)
