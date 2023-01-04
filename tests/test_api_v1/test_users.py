from dataclasses import dataclass
from typing import Union

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.errors.errors import ManagedErrors
from app.core.schemas.errors import Error, ErrorList
from app.core.schemas.users import (
    UserInDB,
    UserInCreate,
    UserWithToken,
    User,
    UserInUpdate,
)
from app.core.strings import APINames
from app.core import jwt
from app.db.errors import EntityDoesNotExist
from app.db.repositories.users import UsersRepository
from tests.conftest import UserExistenceError
from tests.resources import AssertionStrings, TestParamData


# # 하나의 test case에서 invalid_data가 다를 때 error case도 같이 달라지는 경우를
# # 위해 invalid_data와 expected_errors를 결합
# @dataclass
# class ErrorCases:
#     invalid_data: dict[str, str]
#     expected_errors: Union[Error, list[Error]]
#

# @pytest.fixture(params=TestParamData.invalid_email_values)
# def invalid_email(request) -> ErrorCases:
#     return ErrorCases({"email": request.param}, ManagedErrors.invalid_email)
#
#
# @pytest.fixture(params=TestParamData.invalid_username_values)
# def invalid_username(request) -> ErrorCases:
#     return ErrorCases({"username": request.param}, ManagedErrors.invalid_email)
#
#
# @pytest.fixture(params=TestParamData.invalid_password_values)
# def invalid_password(request) -> ErrorCases:
#     return ErrorCases(
#         {"password": request.param}, ManagedErrors.invalid_password
#     )
#
#
# @pytest.fixture(
#     params=[
#         invalid_email,
#         invalid_username,
#         invalid_password,
#     ]
# )
# def invalid_user_field(request) -> ErrorCases:
#     return request.param


@pytest.fixture
def unique_user_in_create() -> UserInCreate:
    return UserInCreate(
        email="unique@uni.que",
        username="unique",
        password="uniquep@ssw0rd",
    )


@pytest.fixture
def unique_user_teardown(
    unique_user_in_create: UserInCreate,
    users_repo: UsersRepository,
):
    yield

    with pytest.raises(EntityDoesNotExist):
        user_in_db = users_repo.get_user_by_email(unique_user_in_create.email)
        users_repo.delete_user(user_in_db.id)
        print(f"TEARDOWN unique user is deleted - id={user_in_db.id}")


@pytest.fixture
def user_pre_teardown(
    test_user_in_create: UserInCreate,
    users_repo: UsersRepository,
) -> None:
    try:
        user_in_db = users_repo.get_user_by_email(test_user_in_create.email)
    except EntityDoesNotExist:
        raise UserExistenceError(
            f"user with email={test_user_in_create.email} does not exists"
        )
    else:
        users_repo.delete_user(user_in_db.id)


# unique_user_in_create = UserInCreate(
#     email="unique@uni.que",
#     username="unique",
#     password="uniquep@ssw0rd",
# )


# @pytest.fixture(
#     params=[
#         {"email": unique_user_in_create.email},
#         {"username": unique_user_in_create.username}.
#     ]
# )
# def unique_user_field(request) -> dict[str, str]:
#     return request.param


@pytest.fixture(
    params=[
        *[
            ({"email": invalid_email_value}, ManagedErrors.invalid_email)
            for invalid_email_value in TestParamData.invalid_email_values
        ],
        *[
            (
                {"username": invalid_username_value},
                ManagedErrors.invalid_username,
            )
            for invalid_username_value in TestParamData.invalid_username_values
        ],
        *[
            (
                {"password": invalid_password_value},
                ManagedErrors.invalid_password,
            )
            for invalid_password_value in TestParamData.invalid_password_values
        ],
    ]
)
def invalid_user_field_with_expected_error(request) -> tuple:
    # todo how to pass invalid user field and error
    raise NotImplementedError


# POST /v1/users
# 신규 유저를 생성합니다.
class TestV1UsersPOST:

    # 유효하지 않은 구문 형식으로 요청 불가
    @pytest.mark.parametrize(
        "invalid_user_in_create",
        TestParamData.user_fields_with_invalid_syntax,
    )
    def test_cannot_create_user_with_invalid_syntax(
        self,
        app: FastAPI,
        client: TestClient,
        invalid_user_in_create: dict,
    ):
        print(f"attempting to create user with invalid syntax")

        response = client.post(
            app.url_path_for(APINames.USERS_CREATE_USER_POST),
            json=invalid_user_in_create,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), AssertionStrings.status_code(status.HTTP_400_BAD_REQUEST)
        assert response.json() == ErrorList(
            ManagedErrors.bad_request
        ), AssertionStrings.errors(ManagedErrors.bad_request)

    # 유효하지 않은 유저 정보 필드값으로 유저 생성 불가
    @pytest.mark.parametrize(
        "invalid_user_field, expected_error",
        [
            # (
            #     {"email": TestParamData.invalid_email_values},
            #     ManagedErrors.invalid_email,
            # ),
            # (
            #     {"username": TestParamData.invalid_username_values},
            #     ManagedErrors.invalid_username,
            # ),
            # (
            #     {"password": TestParamData.invalid_password_values},
            #     ManagedErrors.invalid_password,
            # ),
            *[
                ({"email": invalid_email_value}, ManagedErrors.invalid_email)
                for invalid_email_value in TestParamData.invalid_email_values
            ],
            *[
                (
                    {"username": invalid_username_value},
                    ManagedErrors.invalid_username,
                )
                for invalid_username_value in TestParamData.invalid_username_values
            ],
            *[
                (
                    {"password": invalid_password_value},
                    ManagedErrors.invalid_password,
                )
                for invalid_password_value in TestParamData.invalid_password_values
            ],
        ],
    )
    def test_cannot_create_user_with_invalid_field(
        self,
        app: FastAPI,
        test_user_in_create: UserInCreate,
        client: TestClient,
        invalid_user_field: dict[str, str],
        expected_error: Error,
    ):
        request_json = test_user_in_create.dict()
        request_json.update(invalid_user_field)

        print(
            "attempting to create user with invalid field"
            f" - request_json={request_json}"
        )
        response = client.post(
            app.url_path_for(APINames.USERS_CREATE_USER_POST),
            json=request_json,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), AssertionStrings.status_code(status.HTTP_400_BAD_REQUEST)
        assert (
            response.json() == ErrorList(expected_error).dict()
        ), AssertionStrings.errors(expected_error)

    # 중복된 필드값으로 유저 생성 요청 불가
    @pytest.mark.parametrize(
        "duplicated_user_field, expected_error",
        [
            (
                {"email": TestParamData.test_user_in_create.email},
                ManagedErrors.duplicated_email,
            ),
            (
                {"username": TestParamData.test_user_in_create.username},
                ManagedErrors.duplicated_username,
            ),
        ],
    )
    def test_cannot_create_user_with_duplicated_field(
        self,
        app: FastAPI,
        user: UserInDB,
        unique_user_in_create: UserInCreate,
        unique_user_teardown: None,
        client: TestClient,
        duplicated_user_field: dict[str, str],
        expected_error: Error,
    ):
        request_json = unique_user_in_create.dict()
        request_json.update(duplicated_user_field)

        print(
            "attempting to create user"
            f" with duplicated field - request_json={request_json}"
        )
        response = client.post(
            app.url_path_for(APINames.USERS_CREATE_USER_POST),
            json=request_json,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), AssertionStrings.status_code(status.HTTP_400_BAD_REQUEST)
        assert (
            response.json() == ErrorList(expected_error).dict()
        ), AssertionStrings.errors(expected_error)

    # # 유효하지 않거나 중복된 여러 필드값들로 요청 불가
    # def test_cannot_create_user_with_multiple_wrong_fields(
    #     self,
    #     app: FastAPI,
    #     user: UserInDB,
    # ):
    #     # todo

    # 유저 생성 요청 가능
    def test_can_create_user(
        self,
        app: FastAPI,
        test_user_in_create: UserInCreate,
        client: TestClient,
    ):
        request_json = test_user_in_create.json()

        print(f"attempting to create user - request_json={request_json}")
        response = client.post(
            app.url_path_for(APINames.USERS_CREATE_USER_POST),
            json=request_json,
        )

        response_model = UserWithToken(**response.json())
        user_from_token = jwt.get_user_from_token(response_model.token)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), AssertionStrings.status_code(status.HTTP_201_CREATED)
        assert response_model.user.email == test_user_in_create.email
        assert response_model.user.username == test_user_in_create.username
        assert user_from_token.dict() == response_model.user.dict()


# GET /v1/users/{user_id}
# 특정 유저 정보를 가져옵니다.
class TestV1UsersRetrieveUserGET:

    # 유효하지 않은 user_id로 요청 불가
    @pytest.mark.parametrize(
        "invalid_user_id",
        TestParamData.invalid_user_id,
    )
    def test_cannot_retrieve_user_with_invalid_syntax(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        invalid_user_id: str,
    ):
        print(
            "attempting to retrieve user with invalid syntax"
            f" - invalid_user_id={invalid_user_id!r}"
        )
        response = client.get(
            app.url_path_for(
                APINames.USERS_RETRIEVE_USER_GET, user_id=invalid_user_id
            )
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), AssertionStrings.status_code(status.HTTP_400_BAD_REQUEST)
        assert (
            response.json() == ErrorList(ManagedErrors.bad_request).dict()
        ), AssertionStrings.errors(ManagedErrors.bad_request)

    # 존재하지 않는 유저의 id로 요청 불가
    def test_cannot_retrieve_user_with_nonexisting_users_id(
        self,
        app: FastAPI,
        user_setup: UserInDB,
        user_pre_teardown: None,
        client: TestClient,
    ):
        print(
            "attempting to retrieve user with"
            f" nonexisting user's id - id={user_setup.id}"
        )
        response = client.get(
            app.url_path_for(
                APINames.USERS_RETRIEVE_USER_GET, user_id=user_setup.id
            )
        )

        assert (
            response.status_code == status.HTTP_404_NOT_FOUND
        ), AssertionStrings.status_code(status.HTTP_404_NOT_FOUND)
        assert (
            response.json() == ErrorList(ManagedErrors.not_found).dict()
        ), AssertionStrings.errors(ManagedErrors.bad_request)

    # 유저 정보 요청 가능
    def test_can_retrieve_user(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        print(f"attempting to retrieve user - id={user.id}")
        response = client.get(
            app.url_path_for(APINames.USERS_RETRIEVE_USER_GET, user_id=user.id)
        )

        assert (
            response.status_code == status.HTTP_200_OK
        ), AssertionStrings.status_code(status.HTTP_200_OK)
        assert response.json() == User(**user.dict()).dict()


class TestV1UsersUpdateUserPATCH:
    @pytest.fixture
    def valid_test_user_in_update(
        self, user: UserInDB, unique_user_in_create: UserInCreate
    ) -> UserInUpdate:
        return UserInUpdate(
            id=user.id,
            username=unique_user_in_create.username,
        )

    @pytest.fixture(params=TestParamData.user_fields_with_invalid_syntax)
    def user_in_update_with_invalid_syntax(
        self, request, user: UserInDB
    ) -> UserInUpdate:
        return UserInUpdate(
            id=user.id,
            **request.param,
        )

    @pytest.fixture(
        params=[
            TestParamData.invalid_email_values,
            TestParamData.invalid_username_values,
            TestParamData.invalid_password_values,
        ]
    )

    # 유효하지 않은 구문 형식으로 요청 불가
    def test_cannot_update_user_with_invalid_syntax(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        user_in_update_with_invalid_syntax: UserInUpdate,
    ):
        request_json = user_in_update_with_invalid_syntax.dict()
        print(
            "attempting to update user with invalid syntax"
            f" - user_in_update={user_in_update_with_invalid_syntax}"
        )
        response = client.patch(
            app.url_path_for(APINames.USERS_UPDATE_USER_PATCH),
            json=request_json,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), AssertionStrings.status_code(status.HTTP_400_BAD_REQUEST)
        assert (
            response.json() == ErrorList(ManagedErrors.bad_request).dict()
        ), AssertionStrings.errors(ManagedErrors.bad_request)

    # Authorization header 없이 요청 불가
    def test_cannot_update_user_without_authorization_header(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        valid_test_user_in_update: UserInUpdate,
    ):
        request_json = valid_test_user_in_update.dict()
        print("attempting to update user without authorization header")
        response = client.patch(
            app.url_path_for(APINames.USERS_UPDATE_USER_PATCH),
            json=request_json,
        )

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), AssertionStrings.status_code(status.HTTP_401_UNAUTHORIZED)
        assert (
            response.json() == ErrorList(ManagedErrors.unauthorized).dict()
        ), AssertionStrings.errors(ManagedErrors.unauthorized)

    # 유효하지 않은 Authorization header로 요청 불가
    def test_cannot_update_user_with_invalid_authorization_header(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        valid_test_user_in_update: UserInUpdate,
        invalid_authorization_header: dict[str, str],
    ):
        request_json = valid_test_user_in_update.dict()
        client.headers.update(invalid_authorization_header)
        print(
            "attempting to update user with invalid authorization header"
            f" - header: {invalid_authorization_header}"
        )
        response = client.patch(
            app.url_path_for(APINames.USERS_UPDATE_USER_PATCH),
            json=request_json,
        )

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), AssertionStrings.status_code(status.HTTP_401_UNAUTHORIZED)
        assert (
            response.json() == ErrorList(ManagedErrors.unauthorized).dict()
        ), AssertionStrings.errors(ManagedErrors.unauthorized)

    # access token payload의 유저 id와 body parameter의 유저 id가 다른 경우 요청 불가
    # def test_cannot_update_user_

    # 해당 유저의 업데이트 쿨다운이 끝나기 전에 요청 불가

    # 유효하지 않은 유저 정보 필드값으로 요청 불가
    def test_cannot_update_user_with_invalid_field(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        ...
