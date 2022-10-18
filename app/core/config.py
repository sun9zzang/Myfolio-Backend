from pydantic import BaseSettings


def get_secret() -> list:
    pass
    # todo boto3


class Settings(BaseSettings):
    APP_ENV: str = "dev"

    # DB connection config
    DB_CONNECTION_STRING = ""  # todo security

    # JWT authentication config
    JWT_TOKEN_PREFIX = "Token"
    JWT_SUBJECT = "access"
    ALGORITHM = "HS256"
    SECRET_KEY = ""  # todo security
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


settings = Settings()
