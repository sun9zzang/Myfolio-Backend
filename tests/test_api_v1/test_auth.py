import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.schemas.users import User, UserInDB, UserWithToken
from app.core.schemas.errors import ErrorList
from app.core.errors.errors import ManagedErrors
from app.core.strings import APINames
from app.core import jwt
from tests.resources import AssertionStrings, TestParamData


# POST /v1/auth/login
# 유저 로그인 API
class TestV1AuthLoginPOST:
    @pytest.fixture
    def login_json(self, user_dict: dict) -> dict:
        return {
            "email": user_dict["email"],
            "password": user_dict["password"],
        }

    # 1. wrong credentials로 로그인 불가
    @pytest.mark.parametrize(
        "wrong_credential_items",
        TestParamData.wrong_credential_items,
    )
    def test_cannot_login_with_wrong_credentials(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        login_json: dict,
        wrong_credential_items: dict,
    ):
        login_json.update(wrong_credential_items)
        print(f"attempting to login with login_json={login_json}")
        response = client.post(
            app.url_path_for(APINames.AUTH_LOGIN_POST),
            json=login_json,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), AssertionStrings.status_code(status.HTTP_400_BAD_REQUEST)
        assert (
            response.json() == ErrorList(ManagedErrors.invalid_credentials).dict()
        ), AssertionStrings.errors(ManagedErrors.invalid_credentials)

    # 2. test user credentials로 로그인 가능
    def test_can_login(
        self,
        app: FastAPI,
        user: UserInDB,
        user_dict: dict,
        client: TestClient,
        login_json: dict,
    ):
        print(f"attempting to login with login_json={login_json}")
        response = client.post(
            app.url_path_for(APINames.AUTH_LOGIN_POST),
            json=login_json,
        )

        assert response.status_code == status.HTTP_200_OK, AssertionStrings.status_code(
            status.HTTP_200_OK
        )
        assert (
            response.json().get("user") == user_dict
        ), "Response Body의 user object가 유효해야 합니다."

        token_in_response = response.json().get("token")
        user_from_token = jwt.get_user_from_token(token_in_response)
        print(f"token_in_response: {token_in_response}")

        assert user_from_token.dict() == user_dict, "발급된 토큰이 유효해야 합니다."


# GET /v1/auth/user-retriever
# 토큰으로 유저 정보를 가져오는 API
class TestV1AuthUserRetrieverGET:

    # 1. Authorization header 없이 유저 정보 요청 불가
    def test_cannot_retrieve_user_without_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        print("attempting to retrieve user data without authorization header...")
        response = client.get(app.url_path_for(APINames.AUTH_USER_RETRIEVER_GET))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), AssertionStrings.status_code(status.HTTP_401_UNAUTHORIZED)
        assert (
            response.json() == ErrorList(ManagedErrors.unauthorized).dict()
        ), AssertionStrings.errors(ManagedErrors.unauthorized)

    # 2. 유효하지 않은 인증 정보로 유저 정보 요청 불가
    def test_cannot_retrieve_user_with_invalid_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
        invalid_authorization_header: dict,
    ):
        client.headers.update(invalid_authorization_header)
        print(
            "header with invalid token is appended"
            f" to the request context - header={invalid_authorization_header}"
        )

        print("attempting to retrieve user data...")
        response = client.get(app.url_path_for(APINames.AUTH_USER_RETRIEVER_GET))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), AssertionStrings.status_code(status.HTTP_401_UNAUTHORIZED)
        assert (
            response.json() == ErrorList(ManagedErrors.unauthorized).dict()
        ), AssertionStrings.errors(ManagedErrors.unauthorized)

    # 3. 유효한 토큰으로 유저 정보 요청 가능
    def test_can_retrieve_user_with_token(
        self,
        app: FastAPI,
        user: UserInDB,
        user_with_token: UserWithToken,
        authorized_client: TestClient,
    ):
        print("attempting to retrieve user data...")
        response = authorized_client.get(
            app.url_path_for(APINames.AUTH_USER_RETRIEVER_GET)
        )
        response_body_dict = response.json()

        assert response.status_code == status.HTTP_200_OK, AssertionStrings.status_code(
            status.HTTP_200_OK
        )
        assert (
            response_body_dict["user"] == User(**user.dict()).dict()
        ), "HTTP response body의 유저 정보가 일치해야 합니다."
        # todo response model
        assert (
            jwt.get_user_from_token(response_body_dict["token"])
            == User(**user.dict()).dict()
        ), "HTTP response body의 token이 유효해야 합니다."


# GET /v1/auth/renew-token
# 기존 토큰을 새로운 토큰으로 갱신하는 API
class TestV1AuthRenewTokenGET:

    # 1. Authorization header 없이 토큰 갱신 요청 불가
    def test_cannot_renew_token_without_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        print("attempting to renew token without authorization header...")
        response = client.get(app.url_path_for(APINames.AUTH_RENEW_TOKEN_GET))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), AssertionStrings.status_code(status.HTTP_401_UNAUTHORIZED)
        assert (
            response.json() == ErrorList(ManagedErrors.unauthorized).dict()
        ), AssertionStrings.errors(ManagedErrors.unauthorized)

    # 2. 유효하지 않은 인증 정보로 토큰 갱신 요청 불가
    def test_cannot_renew_token_with_invalid_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
        invalid_authorization_header: dict,
    ):
        client.headers.update(invalid_authorization_header)
        print(
            "header with invalid token is appended"
            f" to the request context - header={invalid_authorization_header}"
        )

        print("attempting to renew token...")
        response = client.get(app.url_path_for(APINames.AUTH_RENEW_TOKEN_GET))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), AssertionStrings.status_code(status.HTTP_401_UNAUTHORIZED)
        assert (
            response.json() == ErrorList(ManagedErrors.unauthorized).dict()
        ), AssertionStrings.errors(ManagedErrors.unauthorized)

    # 3. 유효한 인증 정보로 토큰 갱신 가능
    def test_can_renew_token(
        self,
        app: FastAPI,
        user_dict: dict,
        authorized_client: TestClient,
    ):
        print("attempting to renew token...")
        response = authorized_client.get(
            app.url_path_for(APINames.AUTH_RENEW_TOKEN_GET)
        )

        # todo response model

        token_in_response = response.json()["token"]
        user_from_token = jwt.get_user_from_token(token_in_response)
        print(f"token_in_response: {token_in_response}")

        assert (
            response.status_code == status.HTTP_200_OK
        ), "HTTP response status code가 '200 OK'여야 합니다."
        assert user_from_token.dict() == user_dict, "갱신된 토큰이 유효해야 합니다."
