import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.schemas.users import UserInDB


@pytest.mark.skip
def test_cannot_register_with_invalid_field():
    pass


@pytest.mark.parametrize("field_name", ["email", "username"])
def test_cannot_register_with_existing_field(
    app: FastAPI,
    user_data: dict,
    user: UserInDB,
    client: TestClient,
    field_name: str,
):
    # unique fields for register
    register_json = {
        "user_in_create": {
            "email": "test_unique@unique.com",
            "username": "test_unique",
            "password": "p@ssw0rd",
        }
    }
    register_json["user_in_create"].update({field_name: user_data[field_name]})
    print(f"register_json: {register_json}")
    response = client.post(
        app.url_path_for("auth:register"),
        json=register_json,
    )
    print(f"response body: {response.json()}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST, "HTTP response status code should be 400"


def test_can_register(
    app: FastAPI,
    user_data: dict,
    user_teardown: None,
    client: TestClient,
):
    register_json = {"user_in_create": user_data}
    print(f"register_json: {register_json}")
    response = client.post(
        app.url_path_for("auth:register"),
        json=register_json,
    )
    print(f"response body: {response.json()}")

    assert response.status_code == status.HTTP_201_CREATED, "HTTP response status code should be 201"
