from enum import Enum

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.application import get_application
from app.core import jwt
from app.core.config import settings
from app.core.schemas.users import UserInCreate, UserInDB
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from app.dependencies.auth import AUTHORIZATION_HEADER_KEY


class UserTestData(Enum):
    email = "test@test.com"
    username = "test_username"
    password = "p@ssw0rd"


class UserExistenceError(Exception):
    ...


@pytest.fixture
def app() -> FastAPI:
    return get_application()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    with TestClient(app) as client:
        print(f"SETUP client generated - client={client!r}")
        yield client
        print("TEARDOWN client")


@pytest.fixture
def user_dict() -> dict:
    # convert UserTestData to dict
    user_data = {i.name: i.value for i in UserTestData}
    return user_data


@pytest.fixture
def users_repo() -> UsersRepository:
    return UsersRepository()


@pytest.fixture
def user_setup(user_dict, users_repo: UsersRepository) -> UserInDB:

    if users_repo.email_exists(UserTestData.email.value):
        raise UserExistenceError(
            f"user with email={UserTestData.email.value!r} already exists"
        )
    if users_repo.username_exists(UserTestData.username.value):
        raise UserExistenceError(
            f"user with username={UserTestData.username.value!r} already exists"
        )

    user_in_create = UserInCreate(**user_dict)
    user_in_db = users_repo.create_user(user_in_create)
    print(f"SETUP user is created - user={user_in_db!r}")

    return user_in_db


@pytest.fixture
def user_teardown(users_repo: UsersRepository) -> None:

    yield

    try:
        user_in_db = users_repo.get_user_by_email(UserTestData.email.value)
    except EntityDoesNotExist:
        raise UserExistenceError(
            f"user with email={UserTestData.email.value} does not exists"
        )
    else:
        users_repo.delete_user(user_in_db.user_id)
        print(f"TEARDOWN user withdrew - user_id={user_in_db.user_id}")


@pytest.fixture
def user(user_setup: UserInDB, user_teardown: None) -> UserInDB:
    yield user_setup


@pytest.fixture
def token(user: UserInDB) -> str:
    token = jwt.create_access_token_for_user(user)
    print(f"token generated for user with user_id={user.user_id} - token={token}")
    return token


@pytest.fixture
def authorization_header_key() -> str:
    return AUTHORIZATION_HEADER_KEY


@pytest.fixture
def authorized_client(
    client: TestClient, token: str, authorization_header_key: str
) -> TestClient:
    header = {authorization_header_key: f"{settings.JWT_TOKEN_PREFIX} {token}"}
    print(f"authorization header is created - header={header}")
    client.headers.update(header)
    print(f"client authorized - client={client!r}")

    return client
