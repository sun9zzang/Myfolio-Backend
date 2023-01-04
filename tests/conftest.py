from datetime import timedelta

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.schemas.users import User, UserInCreate, UserInDB, UserWithToken
from app.core.config import config
from app.core import jwt
from app.db.repositories.users import UsersRepository
from app.db.errors import EntityDoesNotExist
from app.application import get_application
from tests.resources import UserTestData, TestParamData


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
def test_user_in_create() -> UserInCreate:
    # # convert UserTestData to dict
    # return {i.name: i.value for i in UserTestData}
    return TestParamData.test_user_in_create


@pytest.fixture
def users_repo() -> UsersRepository:
    return UsersRepository()


@pytest.fixture
def user_setup(
    test_user_in_create: UserInCreate, users_repo: UsersRepository
) -> UserInDB:

    if users_repo.email_exists(test_user_in_create.email):
        raise UserExistenceError(
            f"user with email={UserTestData.email.value!r} already exists"
        )
    if users_repo.username_exists(test_user_in_create.username):
        raise UserExistenceError(
            f"user with username={UserTestData.username.value!r} already exists"
        )

    user_in_db = users_repo.create_user(test_user_in_create)
    print(f"SETUP user is created - user={user_in_db!r}")

    return user_in_db


@pytest.fixture
def user_teardown(
    test_user_in_create: UserInCreate, users_repo: UsersRepository
) -> None:

    yield

    try:
        user_in_db = users_repo.get_user_by_email(test_user_in_create.email)
    except EntityDoesNotExist:
        raise UserExistenceError(
            f"user with email={UserTestData.email.value} does not exists"
        )
    else:
        users_repo.delete_user(user_in_db.id)
        print(f"TEARDOWN user is deleted - id={user_in_db.id}")


@pytest.fixture
def user(user_setup: UserInDB, user_teardown: None) -> UserInDB:
    yield user_setup


@pytest.fixture
def token(user: UserInDB) -> str:
    token = jwt.create_access_token_for_user(user)
    print(f"token generated for user with id={user.id} - token={token}")
    return token


@pytest.fixture
def user_with_token(user: UserInDB, token: str) -> UserWithToken:
    return UserWithToken(
        user=User(**user.dict()),
        token=token,
    )


@pytest.fixture
def authorized_client(
    client: TestClient,
    token: str,
) -> TestClient:
    header = {"Authorization": f"{config.JWT_TOKEN_PREFIX} {token}"}
    print(f"authorization header has appended - header={header}")
    client.headers.update(header)
    print(f"client authorized - client={client!r}")

    return client


@pytest.fixture(params=TestParamData.invalid_tokens)
def invalid_token(request) -> str:
    return config.JWT_TOKEN_PREFIX + " " + request.param


@pytest.fixture(params=TestParamData.invalid_token_prefixes)
def token_with_invalid_prefix(request, token: str) -> str:
    return request.param + " " + token


@pytest.fixture
def expired_token(user: UserInDB) -> str:
    # 1분 전에 만료된 토큰
    return jwt.create_jwt_token(
        jwt_content=User(**user.dict()).dict(),
        secret_key=config.JWT_SECRET_KEY,
        expires_delta=timedelta(minutes=-1),
    )


@pytest.fixture(
    params=[
        invalid_token,
        token_with_invalid_prefix,
        expired_token,
    ]
)
def invalid_authorization_header(request) -> dict:
    return {"Authorization": request.param}
