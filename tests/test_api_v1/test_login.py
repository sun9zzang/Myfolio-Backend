import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.schemas.users import UserInDB
from tests.conftest import UserTestData


@pytest.mark.parametrize(
    "credentials_field, credentials_value",
    [
        (UserTestData.email.name, "wrong_email@wrong.com"),
        (UserTestData.password.name, "wrong_p@ssw0rd"),
    ],
)
def test_cannot_login_with_wrong_credentials(
    app: FastAPI,
    user: UserInDB,
    client: TestClient,
    credentials_field: str,
    credentials_value: str,
):
    login_json = {
        "user_in_login": {
            UserTestData.email.name: UserTestData.email.value,
            UserTestData.password.name: UserTestData.password.value,
        }
    }
    login_json["user_in_login"].update({credentials_field: credentials_value})
    print(f"login_json: {login_json}")

    response = client.post(
        app.url_path_for("auth:login"),
        json=login_json,
    )
    print(f"response body: {response.json()}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, "HTTP response status code should be 400"


def test_can_login(
    app: FastAPI,
    user_data: dict,
    user: UserInDB,
    client: TestClient,
):
    login_json = {"user_in_login": user_data}
    print(f"login_json: {login_json}")

    response = client.post(
        app.url_path_for("auth:login"),
        json=login_json,
    )
    print(f"response body: {response.json()}")

    assert response.status_code == status.HTTP_200_OK, "HTTP response status code should be 200"
