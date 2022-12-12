import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.errors.errors import ManagedErrors
from app.core.schemas.errors import Error, ErrorList
from app.core.schemas.users import UserInDB
from app.core.strings import APINames
from app.core import jwt
from tests.resources import AssertionStrings, TestParamData


# @pytest.fixture(
#     params=[
#         {"email": TestParamData.invalid_email_values},
#         {"username": TestParamData.invalid_username_values},
#         {"password": TestParamData.invalid_password_values},
#     ]
# )
# def invalid_user_field_param(request) -> dict:
#     return request.param


# POST /v1/users
# 신규 유저를 생성합니다.
class TestV1UsersPOST:

    # 1. 유효하지 않은 유저 정보 필드로 유저 생성 불가
    @pytest.mark.parametrize(
        "invalid_user_field, expected_error",
        [
            (
                {"email": TestParamData.invalid_email_values},
                ManagedErrors.invalid_email,
            ),
            (
                {"username": TestParamData.invalid_username_values},
                ManagedErrors.invalid_username,
            ),
            (
                {"password": TestParamData.invalid_password_values},
                ManagedErrors.invalid_password,
            ),
        ],
    )
    def test_cannot_create_user_with_wrong_field(
        self,
        app: FastAPI,
        user_dict: dict,
        client: TestClient,
        invalid_user_field: dict,
        expected_error: Error,
    ):
        user_dict.update(invalid_user_field)
        print(f"attempting to create user with invalid field - user_dict={user_dict}")
        response = client.post(
            app.url_path_for(APINames.USERS_CREATE_USER_POST),
            json=user_dict,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), AssertionStrings.status_code(status.HTTP_400_BAD_REQUEST)
        assert response.json() == ErrorList(
            ManagedErrors.invalid_credentials
        ), AssertionStrings.errors(ManagedErrors.invalid_credentials)

    # 2. 중복된 필드로 유저 생성 요청 불가
    def test_cannot_create_user_with_duplicated_field(
        self,
        app: FastAPI,
        user_dict: dict,
        user: UserInDB,
        client: TestClient,
    ):
        print(
            "attempting to create user"
            f" with duplicated field - user_dict={user_dict}"
        )

        # todo

    # 유효한 필드로 유저 생성 요청 가능
    def test_can_create_user(
        self,
        app: FastAPI,
        user_dict: dict,
        client: TestClient,
    ):
        print(f"attempting to create user - user_dict={user_dict}")
        response = client.post(
            app.url_path_for(APINames.USERS_CREATE_USER_POST),
            json=user_dict,
        )

        user_in_response = response.json()["user"]
        token_in_response = response.json()["token"]
        user_from_token = jwt.get_user_from_token(token_in_response)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), AssertionStrings.status_code(status.HTTP_201_CREATED)
        assert user_in_response["email"] == user_dict["email"]
        assert user_in_response["username"] == user_dict["username"]
        assert user_from_token.email == user_dict["email"]
        assert user_from_token.username == user_dict["username"]


# GET /v1/users/{user_id}
# 유저 정보를 가져옵니다.
class TestV1UsersRetrieveUserGET:

    # 잘못된 user_id로 유저 정보 요청 불가
    @pytest.mark.parametrize(
        "invalid_user_id",
        [
            "abcdef",
            "가나다",
            "?",
        ],
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
            f" - invalid_user_id: {invalid_user_id}"
        )
        response = client.get(
            app.url_path_for("users:retrieve-user", user_id=invalid_user_id)
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST, ""
        assert (
            response.json() == ErrorList().append(ManagedErrors.bad_request).dict()
        ), ""

    # 존재하지 않는 user_id로 유저 정보 요청 불가
    def test_cannot_retrieve_user_with_not_existing_user_id(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        raise NotImplementedError

    # 존재하는 유저 정보 요청 가능
    def test_can_retrieve_user(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        print(f"attempting to retrieve user - user_id: {user.user_id}")
        response = client.get(
            app.url_path_for("users:retrieve-user", user_id=user.user_id)
        )

        assert response.status_code == status.HTTP_200_OK, ""
        assert response.json() == user.dict(
            exclude={"salt": True, "hashed_password": True}
        ), ""


class TestV1UsersUpdateUserPATCH:

    # Authorization header 없이 유저 업데이트 요청 불가
    def test_cannot_update_user_without_authentication(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        print("attempting to update user without authentication...")

        raise NotImplementedError

    # 유효하지 않은 인증 정보로 유저 업데이트 요청 불가
    def test_cannot_update_user_with_invalid_authentication(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        authorization_header_key: str,
    ):
        header = {authorization_header_key: ...}
        client.headers.update(header)
        print(
            f"attempting to update user with invalid authentication - header: {header}"
        )

        raise NotImplementedError
