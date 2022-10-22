from contextlib import AbstractContextManager, contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.models import base


class DB:
    def __init__(self, connection_string: str, **options) -> None:
        self._engine = create_engine(connection_string, **options)
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


db = DB(settings.DB_CONNECTION_STRING)
