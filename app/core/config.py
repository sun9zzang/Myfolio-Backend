import base64
import json
import os

import boto3
from botocore.exceptions import ClientError
from pydantic import BaseSettings


def get_secret() -> dict:
    secret_name = "Myfolio"
    region_name = "ap-northeast-2"

    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        region_name=region_name,
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text
            # using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid
            # for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Secrets Manager decrypts the secret value
        # using the associated KMS CMK
        # Depending on whether the secret was a string or binary,
        # only one of these fields will be populated
        if "SecretString" in get_secret_value_response:
            secret_data = get_secret_value_response["SecretString"]
        else:
            secret_data = base64.b64decode(get_secret_value_response["SecretBinary"])

        return json.loads(secret_data)


# secrets stored in AWS Secrets Manager
secrets: dict = get_secret()


class GlobalConfig(BaseSettings):

    # datetime precision
    # 3 -> milliseconds, 6 -> microseconds
    DATETIME_PRECISION = 6

    # User config
    USERS_EMAIL_MAX_LENGTH = 254
    USERS_EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    USERS_USERNAME_MIN_LENGTH = 2
    USERS_USERNAME_MAX_LENGTH = 32

    # Templates config
    TEMPLATES_LIST_DEFAULT_ITEM_LIMIT = 20
    TEMPLATES_LIST_MIN_ITEM_LIMIT = 1
    TEMPLATES_LIST_MAX_ITEM_LIMIT = 100
    TEMPLATE_TITLE_MIN_LENGTH = 2
    TEMPLATE_TITLE_MAX_LENGTH = 50

    # JWT authentication config
    JWT_TOKEN_PREFIX = "Bearer"
    JWT_SUBJECT = "access"
    JWT_ALGORITHM = "HS256"
    JWT_SECRET_KEY = secrets["jwt_secret_key"]
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30


class DevConfig(GlobalConfig):
    ENV_STATE = "dev"

    # DB connection settings
    MYSQL_DSN: str = secrets["mysql_dsn_dev"]


class TestConfig(GlobalConfig):
    ENV_STATE = "test"

    # DB connection settings
    MYSQL_DSN: str = secrets["mysql_dsn_test"]


class ProdConfig(GlobalConfig):
    ENV_STATE = "prod"

    # DB connection settings
    MYSQL_DSN: str = secrets["mysql_dsn_prod"]


class FactoryConfig:
    def __init__(self, env_state: str):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == "prod":
            return ProdConfig()
        elif self.env_state == "dev":
            return DevConfig()
        elif self.env_state == "test":
            return TestConfig()
        else:
            raise ValueError


config = FactoryConfig(os.environ.get("ENV_STATE", "dev"))()
