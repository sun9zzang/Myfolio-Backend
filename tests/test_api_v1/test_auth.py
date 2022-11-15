from datetime import timedelta

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.schemas.users import User, UserInDB
from app.core.schemas.errors import ErrorList
from app.core.errors.errors import ManagedErrors
from app.core.config import settings
from app.core import jwt


class _TestParamData:
    invalid_tokens = [
        "iamnottoken",
        "youthinkiamrealtoken??",
        "토큰토큰토큰토작은토큰얼큰토큰",
    ]
    invalid_token_prefixes = [
        "iamnotprefix",
        "Basic",
        "Digest",
        "Token",
        "JWT",
    ]


@pytest.fixture
def expired_token(user: UserInDB) -> str:
    # 1분 전에 만료된 토큰
    return jwt.create_jwt_token(
        jwt_content=User(**user.dict()).dict(),
        secret_key=settings.JWT_SECRET_KEY,
        expires_delta=timedelta(minutes=-1),
    )


@pytest.fixture(params=[*_TestParamData.invalid_tokens, expired_token])
def invalid_token(request) -> str:
    return request.params


@pytest.fixture(params=_TestParamData.invalid_token_prefixes)
def invalid_token_prefix(request) -> str:
    return request.params


# POST /v1/auth/login
# 유저 로그인 API
class TestV1AuthLoginPOST:
    @pytest.fixture
    def login_json(self, user_dict) -> dict:
        return {
            "email": user_dict["email"],
            "password": user_dict["password"],
        }

    # wrong credentials로 로그인 불가
    @pytest.mark.parametrize(
        "credential_item",
        [
            {"email": "wrong@example.com"},
            {"password": "wrong_p@ssw0rd"},
            {"email": "wrong@example.com", "password": "wrong_p@ssw0rd"},
        ],
    )
    def test_cannot_login_with_wrong_credentials(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        login_json: dict,
        credential_item: dict,
    ):
        login_json.update(credential_item)
        print(f"attempting to login with login_json={login_json}")
        response = client.post(
            app.url_path_for("auth:login"),
            json=login_json,
        )

        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), "HTTP response status code가 '400 Bad Request'여야 합니다."
        assert response.json() == ErrorList().append(ManagedErrors.invalid_credentials).dict(),\
            "Error code가 'invalid_credentials'여야 합니다."

    # test user credentials로 로그인 가능
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
            app.url_path_for("auth:login"),
            json=login_json,
        )

        assert (
            response.status_code == status.HTTP_200_OK
        ), "HTTP response status code가 '200 OK'여야 합니다."
        assert response.json()["user"] == user_dict, "Response Body의 user object가 유효해야 합니다."

        token_in_response = response.json()["token"]
        user_from_token = jwt.get_user_from_token(token_in_response)
        print(f"token_in_response: {token_in_response}")

        assert user_from_token.dict() == user_dict, "발급된 토큰이 유효해야 합니다."


# GET /v1/auth/user-retriever
# 토큰으로 유저 정보를 가져오는 API
class TestV1AuthUserRetrieverGET:

    # Authorization header 없이 유저 정보 요청 불가
    def test_cannot_retrieve_user_without_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        print("attempting to retrieve user data without authorization header...")
        response = client.get(app.url_path_for("auth:user-retriever"))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 '401 Unauthorized'여야 합니다."
        assert response.json() == ErrorList().append(ManagedErrors.unauthorized).dict(),\
            "Error code가 'unauthorized'여야 합니다."

    # 유효하지 않은 토큰으로 유저 정보 요청 불가
    def test_cannot_retrieve_user_with_invalid_token(
        self,
        app: FastAPI,
        client: TestClient,
        authorization_header_key: str,
        invalid_token: str,
    ):
        header = {authorization_header_key: f"{settings.JWT_TOKEN_PREFIX} {invalid_token}"}
        client.headers.update(header)
        print(f"header with invalid token is appended to the request context - header={header}")

        print("attempting to retrieve user data...")
        response = client.get(app.url_path_for("auth:user-retriever"))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 '401 Unauthorized'여야 합니다."
        assert response.json() == ErrorList().append(ManagedErrors.unauthorized).dict(),\
            "Error code가 'unauthorized'여야 합니다."

    # 유효하지 않은 token prefix로 유저 정보 요청 불가
    def test_cannot_retrieve_user_with_invalid_token_prefix(
        self,
        app: FastAPI,
        client: TestClient,
        token: str,
        authorization_header_key: str,
        invalid_token_prefix: str,
    ):
        header = {authorization_header_key: f"{invalid_token_prefix} {token}"}
        client.headers.update(header)
        print(f"header with invalid token prefix is appended to the request context - header={header}")

        print("attempting to retrieve user data...")
        response = client.get(app.url_path_for("auth:user-retriever"))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 '401 Unauthorized'여야 합니다."
        assert response.json() == ErrorList().append(ManagedErrors.unauthorized).dict(),\
            "Error code가 'unauthorized'여야 합니다."

    # 유효한 토큰으로 유저 정보 요청 가능
    def test_can_retrieve_user_with_token(
        self,
        app: FastAPI,
        user_dict,
        authorized_client: TestClient,
    ):
        print("attempting to retrieve user data...")
        response = authorized_client.get(app.url_path_for("auth:user-retriever"))

        assert (
            response.status_code == status.HTTP_200_OK
        ), "HTTP response status code가 '200 OK'여야 합니다."
        assert response.json() == user_dict, "Response Body의 유저 정보가 유효해야 합니다."


# GET /v1/auth/renew-token
# 기존 토큰을 새로운 토큰으로 갱신하는 API
class TestV1AuthRenewTokenGET:

    # Authorization header 없이 토큰 갱신 요청 불가
    def test_cannot_renew_token_without_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        print("attempting to renew token without authorization header...")
        response = client.get(app.url_path_for("auth:renew-token"))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 '401 Unauthorized'여야 합니다."
        assert response.json() == ErrorList().append(ManagedErrors.unauthorized).dict(),\
            "Error code가 'unauthorized'여야 합니다."

    # 유효하지 않은 토큰으로 토큰 갱신 요청 불가
    def test_cannot_renew_token_with_invalid_token(
        self,
        app: FastAPI,
        client: TestClient,
        authorization_header_key: str,
        invalid_token: str,
    ):
        header = {authorization_header_key: f"{settings.JWT_TOKEN_PREFIX} {invalid_token}"}
        client.headers.update(header)
        print(f"header with invalid token is appended to the request context - header={header}")

        print("attempting to renew token...")
        response = client.get(app.url_path_for("auth:renew-token"))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 '401 Unauthorized'여야 합니다."
        assert response.json() == ErrorList().append(ManagedErrors.unauthorized).dict(), \
            "Error code가 'unauthorized'여야 합니다."

    # 유효하지 않은 token prefix로 토큰 갱신 요청 불가
    def test_cannot_renew_token_with_invalid_token_prefix(
        self,
        app: FastAPI,
        client: TestClient,
        token: str,
        authorization_header_key: str,
        invalid_token_prefix: str,
    ):
        header = {authorization_header_key: f"{invalid_token_prefix} {token}"}
        client.headers.update(header)
        print(f"header with invalid token prefix is appended to the request context - header={header}")

        print("attempting to renew token...")
        response = client.get(app.url_path_for("auth:renew-token"))

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 '401 Unauthorized'여야 합니다."
        assert response.json() == ErrorList().append(ManagedErrors.unauthorized).dict(), \
            "Error code가 'unauthorized'여야 합니다."

    # 유효한 토큰으로 토큰 갱신 가능
    def test_can_renew_token(
        self,
        app: FastAPI,
        user_dict: dict,
        authorized_client: TestClient,
    ):
        print("attempting to renew token...")
        response = authorized_client.get(app.url_path_for("auth:renew-token"))

        token_in_response = response.json()["token"]
        user_from_token = jwt.get_user_from_token(token_in_response)
        print(f"token_in_response: {token_in_response}")

        assert (
            response.status_code == status.HTTP_200_OK
        ), "HTTP response status code가 '200 OK'여야 합니다."
        assert user_from_token.dict() == user_dict, "갱신된 토큰이 유효해야 합니다."
