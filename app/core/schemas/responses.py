from typing import Optional, Type, Any

from fastapi import status
from pydantic import BaseModel

from app.core.schemas.errors import Error, ErrorList
from app.core.schemas.users import User, UserWithToken
from app.core.strings import ErrorStrings


def get_schema(
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


class _ExampleDatas:
    user = User(user_id=123456, email="example@exam.ple", username="example").dict()
    token = {"token": "abcde12345"}
    user_with_token = {
        "user": user,
        "token": "abcde12345"
    }


class ResponseSchemaV1:
    class Users:
        CREATE_USER = {
            status.HTTP_201_CREATED: get_schema(
                description="유저 생성에 성공 시 user와 token을 반환합니다.",
                model=UserWithToken,
                example=_ExampleDatas.user_with_token,
            ),
            status.HTTP_400_BAD_REQUEST: get_schema(
                description="요청한 필드 값이 유효하지 않거나 이미 존재해 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.duplicated_email.value,
                            code=ErrorStrings.duplicated_email.name,
                        ).dict(),
                        Error(
                            message=ErrorStrings.invalid_password.value,
                            code=ErrorStrings.invalid_password.name,
                        ).dict()
                    ]
                },
            ),
        }

        RETRIEVE_USER = {
            status.HTTP_200_OK: get_schema(
                description="유저 정보 요청에 성공 시 유저 정보를 반환합니다.",
                model=User,
                example=_ExampleDatas.user_with_token,
            ),
            status.HTTP_404_NOT_FOUND: get_schema(
                description="해당하는 유저를 찾을 수 없을 때 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.user_not_found.value,
                            code=ErrorStrings.user_not_found.name,
                        ),
                    ]
                },
            )
        }

        UPDATE_USER = {
            status.HTTP_200_OK: get_schema(
                description="유저 정보 업데이트에 성공 시 업데이트된 유저 정보를 반환합니다.",
                model=User,
                example=_ExampleDatas.user,
            ),
            status.HTTP_400_BAD_REQUEST: get_schema(
                description="요청한 필드 값이 유효하지 않거나 이미 존재해 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.duplicated_email.value,
                            code=ErrorStrings.duplicated_email.name,
                        ).dict(),
                        Error(
                            message=ErrorStrings.invalid_password.value,
                            code=ErrorStrings.invalid_password.name,
                        ).dict()
                    ]
                },
            ),
            status.HTTP_401_UNAUTHORIZED: get_schema(
                description="업데이트 대상 유저가 인증되지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.unauthorized.value,
                            code=ErrorStrings.unauthorized.name,
                        ),
                    ]
                }
            ),
            status.HTTP_403_FORBIDDEN: get_schema(
                description="업데이트 대상 유저와 인증 정보가 일치하지 않거나 인증 정보가 잘못되어 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.forbidden.value,
                            code=ErrorStrings.forbidden.name,
                        )
                    ]
                },
            ),
        }

        DELETE_USER = {
            status.HTTP_204_NO_CONTENT: get_schema(
                description="유저 삭제에 성공 시 204 No Content를 반환합니다.",
            ),
            status.HTTP_401_UNAUTHORIZED: get_schema(
                description="삭제 대상 유저가 인증되지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.unauthorized.value,
                            code=ErrorStrings.unauthorized.name,
                        ),
                    ]
                },
            ),
            status.HTTP_403_FORBIDDEN: get_schema(
                description="삭제 대상 유저와 인증 정보가 일치하지 않거나 인증 정보가 잘못되어 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.forbidden.value,
                            code=ErrorStrings.forbidden.name,
                        ),
                    ]
                },
            ),
        }

    class Auth:
        LOGIN = {
            status.HTTP_200_OK: get_schema(
                description="유저가 로그인에 성공하면 user와 token을 반환합니다.",
                model=UserWithToken,
                example=_ExampleDatas.user_with_token,
            ),
            status.HTTP_400_BAD_REQUEST: get_schema(
                description="유저 이메일 또는 비밀번호가 유효하지 않을 경우 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.invalid_credentials.value,
                            code=ErrorStrings.invalid_credentials.name,
                        ),
                    ]
                },
            ),
        }

        USER_RETRIEVER = {
            status.HTTP_200_OK: get_schema(
                description="유저 인증 토큰으로부터 유저 정보를 가져옵니다. user를 반환합니다.",
                model=User,
                example=_ExampleDatas.user,
            ),
            status.HTTP_401_UNAUTHORIZED: get_schema(
                description="유저가 인증되지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.unauthorized.value,
                            code=ErrorStrings.unauthorized.name,
                        ),
                    ]
                },
            ),
            status.HTTP_403_FORBIDDEN: get_schema(
                description="유저 인증 정보가 잘못되거나 만료되어 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.forbidden.value,
                            code=ErrorStrings.forbidden.name,
                        ),
                    ]
                },
            ),
        }

        RENEW_TOKEN = {
            status.HTTP_200_OK: get_schema(
                description="기존 유저 인증 토큰을 갱신합니다. token을 반환합니다.",
                example=_ExampleDatas.token,
            ),
            status.HTTP_401_UNAUTHORIZED: get_schema(
                description="유저가 인증되지 않아 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.unauthorized.value,
                            code=ErrorStrings.unauthorized.name,
                        ),
                    ]
                },
            ),
            status.HTTP_403_FORBIDDEN: get_schema(
                description="유저 인증 정보가 잘못되거나 만료되어 에러를 반환합니다.",
                model=ErrorList,
                example={
                    "errors": [
                        Error(
                            message=ErrorStrings.forbidden.value,
                            code=ErrorStrings.forbidden.name,
                        ),
                    ]
                },
            ),
        }
