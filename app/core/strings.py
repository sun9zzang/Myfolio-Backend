# API messages

from enum import Enum


WRONG_CREDENTIALS_ERROR = "이메일 또는 비밀번호를 잘못 입력했습니다. 입력하신 내용을 다시 확인해주세요."

HTTP_400_BAD_REQUEST = "잘못된 요청입니다. 요청 정보를 다시 확인해주세요."
HTTP_401_UNAUTHORIZED_ERROR = "해당 요청을 위한 인증이 필요합니다."
HTTP_403_FORBIDDEN_ERROR = "해당 요청에 대한 권한이 없거나 인증 정보가 유효하지 않습니다."


class ErrorStrings(Enum):

    # 400 Bad Request
    bad_request = "The server cannot process the request due to malformed request payload"

    # 401 Unauthorized
    unauthorized = "The user is not authenticated"

    # 403 Forbidden
    forbidden = "User authentication failed or the user does not have permission for this request"

    # 404 Not Found
    not_found = "The requested resource could not be found"

    # /v1/users
    invalid_email = "Invalid email format"
    duplicated_email = "Email already exists"
    invalid_username = "Invalid username format"
    duplicated_username = "Username already exists"
    invalid_password = "Invalid password format"
    user_not_found = "The requested user could not be found"

    # /v1/auth
    invalid_credentials = "Invalid email or password"

