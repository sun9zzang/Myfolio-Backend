from datetime import timedelta

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.schemas.users import User, UserInDB
from app.core.config import settings
from app.core import strings, jwt


class _TestAuthHeaderData:
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


# POST /v1/auth/login
# 유저 로그인 API
class TestAuthLoginPost:
    @pytest.fixture
    def login_json(self, user_data: dict) -> dict:
        return {
            "email": user_data["email"],
            "password": user_data["password"],
        }

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
        print(f"login with login_json={login_json!r}")

        response = client.post(
            app.url_path_for("auth:login"),
            json=login_json,
        )
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST, "HTTP response status code가 400 Bad Request여야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.WRONG_CREDENTIALS_ERROR,
        }, "에러 정보가 일치해야 합니다."

    def test_can_login(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
        login_json: dict,
    ):
        print(f"login with login_json={login_json!r}")

        response = client.post(
            app.url_path_for("auth:login"),
            json=login_json,
        )
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_200_OK, "HTTP response status code가 200 OK여야 합니다."
        assert response.json()["user"] == {
            "user_id": user.user_id,
            "email": user.email,
            "username": user.username,
        }, "Response Body의 유저 object가 유효해야 합니다."

        token_in_response = response.json()["token"]
        user_in_response = jwt.get_user_from_token(token_in_response)
        assert user_in_response == User(**user.dict()), "Response Body의 토큰이 유효해야 합니다."


# HEAD /v1/auth/user
# 토큰으로 유저 정보를 가져오는 API
class TestAuthUserHead:
    def test_cannot_retrieve_user_without_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        response = client.head(app.url_path_for("auth:user"))
        print(f"response body: {response.json()!r}")

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 401 Unauthorized여야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.UNAUTHORIZED_ERROR,
        }, "에러 정보가 일치해야 합니다."

    @pytest.mark.parametrize(
        "invalid_token",
        _TestAuthHeaderData.invalid_tokens,
    )
    def test_cannot_retrieve_user_with_invalid_token(
        self,
        app: FastAPI,
        client: TestClient,
        invalid_token: str,
    ):
        header = {"Authorization": f"{settings.JWT_TOKEN_PREFIX} {invalid_token}"}
        client.headers.update(header)
        print(f"header with invalid token is appended - header={header!r}")

        response = client.head(app.url_path_for("auth:user"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, "HTTP response status code가 403 Forbidden이어야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.FORBIDDEN_ERROR,
        }, "에러 정보가 일치해야 합니다."

    @pytest.mark.parametrize(
        "invalid_token_prefix",
        _TestAuthHeaderData.invalid_token_prefixes,
    )
    def test_cannot_retrieve_user_with_invalid_token_prefix(
        self,
        app: FastAPI,
        token: str,
        client: TestClient,
        invalid_token_prefix: str,
    ):
        header = {"Authorization": f"{invalid_token_prefix} {token}"}
        client.headers.update(header)
        print(f"header with invalid token prefix is appended - header={header!r}")

        response = client.head(app.url_path_for("auth:user"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, "HTTP response status code가 403 Forbidden이어야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.FORBIDDEN_ERROR,
        }, "에러 정보가 일치해야 합니다."

    def test_cannot_retrieve_user_with_expired_token(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        # 1분 전에 만료된 토큰
        expired_token = jwt.create_jwt_token(
            jwt_content=User(**user.dict()).dict(),
            secret_key=settings.JWT_SECRET_KEY,
            expires_delta=timedelta(minutes=-1),
        )
        header = {"Authorization": f"{settings.JWT_TOKEN_PREFIX} {expired_token}"}
        client.headers.update({"Authorization": f"{settings.JWT_TOKEN_PREFIX} {expired_token}"})
        print(f"header with expired token is appended - header={header!r}")

        response = client.head(app.url_path_for("auth:user"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, "HTTP response status code가 403 Forbidden이어야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.FORBIDDEN_ERROR,
        }, "에러 정보가 일치해야 합니다."

    def test_can_retrieve_user_with_token(
        self,
        app: FastAPI,
        token: str,
        authorized_client: TestClient,
    ):
        response = authorized_client.head(app.url_path_for("auth:user"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_200_OK, "HTTP response status code가 200 OK여야 합니다."
        assert response.json() == {"token": token}


# HEAD /v1/auth/token
# 기존 토큰을 새로운 토큰으로 갱신하는 API
class TestAuthTokenHead:
    def test_cannot_renew_token_without_authorization_header(
        self,
        app: FastAPI,
        client: TestClient,
    ):
        response = client.head(app.url_path_for("auth:token"))
        print(f"response body: {response.json()!r}")

        assert (
            response.status_code == status.HTTP_401_UNAUTHORIZED
        ), "HTTP response status code가 401 Unauthorized여야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.UNAUTHORIZED_ERROR,
        }, "에러 정보가 일치해야 합니다."

    @pytest.mark.parametrize(
        "invalid_token",
        _TestAuthHeaderData.invalid_tokens,
    )
    def test_cannot_renew_token_with_invalid_token(
        self,
        app: FastAPI,
        client: TestClient,
        invalid_token: str,
    ):
        header = {"Authorization": f"{settings.JWT_TOKEN_PREFIX} {invalid_token}"}
        client.headers.update(header)
        print(f"header with invalid token is appended - header={header!r}")

        response = client.head(app.url_path_for("auth:token"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, "HTTP response status code가 403 Forbidden이어야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.UNAUTHORIZED_ERROR,
        }

    @pytest.mark.parametrize(
        "invalid_token_prefix",
        _TestAuthHeaderData.invalid_token_prefixes,
    )
    def test_cannot_renew_token_with_invalid_token_prefix(
        self,
        app: FastAPI,
        token: str,
        client: TestClient,
        invalid_token_prefix: str,
    ):
        header = {"Authorization": f"{invalid_token_prefix} {token}"}
        client.headers.update(header)
        print(f"header with invalid token prefix is appended - header={header!r}")

        response = client.head(app.url_path_for("auth:token"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, "HTTP response status code가 403 Forbidden이어야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.UNAUTHORIZED_ERROR,
        }

    def test_cannot_renew_token_with_expired_token(
        self,
        app: FastAPI,
        user: UserInDB,
        client: TestClient,
    ):
        # 1분 전에 만료된 토큰
        expired_token = jwt.create_jwt_token(
            jwt_content=User(**user.dict()).dict(),
            secret_key=settings.JWT_SECRET_KEY,
            expires_delta=timedelta(minutes=-1),
        )
        header = {"Authorization": f"{settings.JWT_TOKEN_PREFIX} {expired_token}"}
        client.headers.update({"Authorization": f"{settings.JWT_TOKEN_PREFIX} {expired_token}"})
        print(f"header with expired is appended - header={header!r}")

        response = client.head(app.url_path_for("auth:token"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_403_FORBIDDEN, "HTTP response status code가 403 Forbidden이어야 합니다."
        assert response.json() == {
            "type": strings.ErrorTypes.invalid_request_error.value,
            "detail": strings.UNAUTHORIZED_ERROR,
        }

    def test_can_renew_token(
        self,
        app: FastAPI,
        token: str,
        authorized_client: TestClient,
    ):
        response = authorized_client.head(app.url_path_for("auth:token"))
        print(f"response body: {response.json()!r}")

        assert response.status_code == status.HTTP_200_OK, "HTTP response status code가 200 OK여야 합니다."
        assert response.json() == {"token": token}
