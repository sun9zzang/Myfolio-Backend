import os
from functools import lru_cache

from pydantic import BaseSettings


class _AppSettings(BaseSettings):
    class DB:
        db_connection_string = os.environ["DB_CONNECTION_STRING"]


@lru_cache()
def _get_settings() -> _AppSettings:
    return _AppSettings()


settings = _get_settings()
