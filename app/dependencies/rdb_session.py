from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.settings import settings


class DB:
    def __init__(self, connection_string: str, **options):
        self._engine = create_engine(connection_string, **options)
        self._make_session = sessionmaker(bind=self._engine)

    def get_session(self):
        session = self._make_session()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = DB(settings.DB.db_connection_string)
