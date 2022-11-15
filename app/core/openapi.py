from typing import Optional, Type

from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel

from app.core.schemas.users import User, UserWithToken, Token
from app.core.schemas.errors import ErrorList
from app.core.errors.errors import ManagedErrors


def custom_openapi(app: FastAPI) -> dict:
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title="Myfolio API",
            version="0.1.0",
            openapi_version=app.openapi_version,
            description="Myfolio API 문서입니다.",
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=[
                {
                    "name": "Auth",
                    "description": "인증과 관련된 기능을 제공합니다.",
                },
                {
                    "name": "Users",
                    "description": "유저 생성, 정보 가져오기, 업데이트, 삭제와 관련된 기능을 제공합니다.",
                },
            ],
            servers=app.servers,
        )

        try:
            for method_item in app.openapi_schema.get("paths").values():
                for param in method_item.values():
                    responses = param.get("responses")
                    # remove 422 response
                    if "422" in responses:
                        del responses["422"]
        except KeyError:
            pass

        try:
            for schema in list(app.openapi_schema["components"]["schemas"]):
                if schema == "HTTPValidationError" or schema == "ValidationError":
                    del app.openapi_schema["components"]["schemas"][schema]
        except KeyError:
            pass

    return app.openapi_schema


def _get_schema(
    *,
    description: Optional[str] = None,
    media_type: str = "application/json",
    model: Type[BaseModel] = None,
    example: Optional[dict] = None,
) -> dict:
    result = {}
    if description:
        result.update({"description": description})

    result.update({"content": {media_type: {}}})

    if model:
        result.update({"model": model})

    if example:
        result["content"][media_type].update({"example": example})

    return result


class ExampleModelDatas:

    user = {"user_id": 1234567, "email": "myfolio@myfolio.com", "username": "myfolio"}
    user_in_create = {
        "email": "myfolio@myfolio.com",
        "username": "myfolio",
        "password": "myp@ssw0rd",
    }
    user_id = 1234567
    user_in_update = {"username": "ye", "password": "newp@ssw0rd"}
    user_updated = {
        "user_id": 1234567,
        "email": "myfolio@myfolio.com",
        "username": "ye",
    }

    user_in_login = {"email": "myfolio@myfolio.com", "password": "myp@ssw0rd"}
    token = {"token": "abcde12345"}
    token_renewed = {"token": "brandnewtoken<3"}
    user_with_token = {"user": user, **token}


class ResponseSchemaV1:

    # Modify auto-generated openapi.json by FastAPI Application

    class Auth:
        LOGIN = {
            status.HTTP_200_OK: _get_schema(
                description="유저가 로그인에 성공하면 user와 token을 반환합니다.",
                model=UserWithToken,
                example=ExampleModelDatas.user_with_token,
            ),
            status.HTTP_400_BAD_REQUEST: _get_schema(
                description="인증 정보가 유효하지 않아 로그인에 실패하여 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.invalid_credentials,
                    ]
                },
            ),
        }

        USER_RETRIEVER = {
            status.HTTP_200_OK: _get_schema(
                description="유저 인증 토큰으로부터 유저 정보를 가져옵니다. user를 반환합니다.",
                model=User,
                example=ExampleModelDatas.user,
            ),
            status.HTTP_401_UNAUTHORIZED: _get_schema(
                description="유저의 인증 정보가 유효하지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.unauthorized,
                    ]
                },
            ),
        }

        RENEW_TOKEN = {
            status.HTTP_200_OK: _get_schema(
                description="기존 유저 인증 토큰을 갱신합니다. token을 반환합니다.",
                model=Token,
                example=ExampleModelDatas.token_renewed,
            ),
            status.HTTP_401_UNAUTHORIZED: _get_schema(
                description="유저의 인증 정보가 유효하지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.unauthorized,
                    ]
                },
            ),
        }

    class Users:
        CREATE_USER = {
            status.HTTP_201_CREATED: _get_schema(
                description="유저 생성에 성공 시 user와 token을 반환합니다.",
                model=UserWithToken,
                example=ExampleModelDatas.user_with_token,
            ),
            status.HTTP_400_BAD_REQUEST: _get_schema(
                description="요청한 필드 값이 유효하지 않거나 이미 존재해 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.duplicated_username,
                        ManagedErrors.invalid_password,
                    ]
                },
            ),
        }

        RETRIEVE_USER = {
            status.HTTP_200_OK: _get_schema(
                description="유저 정보 요청에 성공 시 유저 정보를 반환합니다.",
                model=User,
                example=ExampleModelDatas.user,
            ),
            status.HTTP_400_BAD_REQUEST: _get_schema(
                description="요청 형식이 잘못되어 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.bad_request,
                    ]
                },
            ),
            status.HTTP_404_NOT_FOUND: _get_schema(
                description="해당하는 유저를 찾을 수 없을 때 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.not_found,
                    ]
                },
            ),
        }

        UPDATE_USER = {
            status.HTTP_200_OK: _get_schema(
                description="유저 정보 업데이트에 성공 시 업데이트된 유저 정보를 반환합니다.",
                model=User,
                example=ExampleModelDatas.user_updated,
            ),
            status.HTTP_400_BAD_REQUEST: _get_schema(
                description="요청한 필드 값이 유효하지 않거나 이미 존재해 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.duplicated_username,
                        ManagedErrors.invalid_password,
                    ]
                },
            ),
            status.HTTP_401_UNAUTHORIZED: _get_schema(
                description="업데이트 대상 유저의 인증 정보가 유효하지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.unauthorized,
                    ]
                },
            ),
            status.HTTP_403_FORBIDDEN: _get_schema(
                description="업데이트 대상 유저와 인증된 유저가 달라 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.forbidden,
                    ]
                },
            ),
        }

        DELETE_USER = {
            status.HTTP_204_NO_CONTENT: _get_schema(
                description="유저 삭제에 성공 시 204 No Content를 반환합니다.",
            ),
            status.HTTP_401_UNAUTHORIZED: _get_schema(
                description="삭제 대상 유저의 인증 정보가 유효하지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.unauthorized,
                    ]
                },
            ),
            status.HTTP_403_FORBIDDEN: _get_schema(
                description="삭제 대상 유저와 인증된 유저가 달라 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        ManagedErrors.forbidden,
                    ]
                },
            ),
        }
