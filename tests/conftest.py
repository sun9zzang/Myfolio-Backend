from enum import Enum

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.schemas.users import UserInCreate, UserInDB
from app.core import jwt
from app.db.repositories.users import UsersRepository
from app.application import get_application


class UserTestData(Enum):
    email = "test_username"
    username = "test@test.com"
    password = "p@ssw0rd"


@pytest.fixture
def app() -> FastAPI:
    return get_application()


@pytest.fixture
def client(app: FastAPI) -> TestClient:
    with TestClient(app) as client:
        print(f"SETUP client generated - client: {client}")
        yield client
        print("TEARDOWN client")


@pytest.fixture
def user_data() -> dict:
    user_data = {i.name: i.value for i in UserTestData}
    print(f"user_data: {user_data}")
    return user_data


@pytest.fixture
def user(user_data) -> UserInDB:
    users_repo = UsersRepository()
    user_in_create = UserInCreate(**user_data)
    user_in_db = await users_repo.create_user(user_in_create)
    print(f"SETUP user is created - {user_in_db}")

    yield user_in_db

    await users_repo.withdraw_user(user_in_db.user_id)
    print(f"TEARDOWN user withdrew - user_id: {user_in_db.user_id}")


@pytest.fixture
def token(user: UserInDB) -> str:
    token = jwt.create_access_token_for_user(user)
    print(f"token generated for user_id: {user.user_id} - token: {token}")
    return token


@pytest.fixture
def authorized_client(client: TestClient, token: str) -> TestClient:
    header = {"Authorization": token}
    client.headers.update(header)
    print(f"header is created for authorization - header: {header}")
    print(f"client authorized - client: {client}")

    return client
