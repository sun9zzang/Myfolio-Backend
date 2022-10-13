from pydantic import BaseSettings


def get_secret() -> list:
    pass
    # todo boto3


class Settings(BaseSettings):
    APP_ENV: str = "dev"

    # DB connection config
    DB_CONNECTION_STRING = ""  # todo security

    # JWT authentication config
    SECRET_KEY: str = ""  # todo security
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()
