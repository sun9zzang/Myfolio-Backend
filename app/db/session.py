from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


class DB:

    def __init__(self, connection_string: str, **options) -> None:
        self._engine = create_engine(connection_string, **options)
        self._sessionmaker = sessionmaker(bind=self._engine)

    def get_session(self) -> Session:
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = DB(settings.DB_CONNECTION_STRING)
