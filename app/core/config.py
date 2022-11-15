import json

import base64
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
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
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
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Secrets Manager decrypts the secret value using the associated KMS CMK
        # Depending on whether the secret was a string or binary, only one of these fields will be populated
        if "SecretString" in get_secret_value_response:
            secret_data = get_secret_value_response["SecretString"]
        else:
            secret_data = base64.b64decode(get_secret_value_response["SecretBinary"])

        return json.loads(secret_data)


class Settings(BaseSettings):
    # stage of application
    APP_ENV: str = "dev"

    # secrets stored in AWS Secrets Manager
    secrets: dict = get_secret()

    # DB connection settings
    DB_CONNECTION_STRING = secrets["rds_connection_string"]

    # datetime precision
    # 3 -> milliseconds, 6 -> microseconds
    DATETIME_PRECISION = 6

    # JWT authentication config
    JWT_TOKEN_PREFIX = "Bearer"
    JWT_SUBJECT = "access"
    ALGORITHM = "HS256"
    JWT_SECRET_KEY = secrets["jwt_secret_key"]
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # User settings
    EMAIL_MAX_LENGTH = 254
    EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    USERNAME_MIN_LENGTH = 2
    USERNAME_MAX_LENGTH = 32

    # Templates settings
    DEFAULT_TEMPLATES_LIST_LIMIT = 20
    TEMPLATES_MIN_LIST_LIMIT = 1
    TEMPLATES_MAX_LIST_LIMIT = 100
    TEMPLATE_TITLE_MIN_LENGTH = 2
    TEMPLATE_TITLE_MAX_LENGTH = 50


settings = Settings()
