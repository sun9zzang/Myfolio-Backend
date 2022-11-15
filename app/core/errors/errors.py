from fastapi import status

from app.core.schemas.errors import Error


class ManagedErrors:

    # Basic managed errors
    # [4xx] HTTP response status codes
    # 400 Bad Request
    bad_request = Error(
        message="The server cannot process the request due to invalid syntax",
        code="bad_request",
    )

    # 401 Unauthorized
    unauthorized = Error(
        message="The user authentication is not valid",
        code="unauthorized",
    )

    # 403 Forbidden
    forbidden = Error(
        message="The request has been passed to the server, but the user does not have enough permission on the request",
        code="forbidden",
    )

    # 404 Not Found
    not_found = Error(
        message="The requested resource could not be found",
        code="not_found",
    )

    # 405 Method Not Allowed
    method_not_allowed = Error(
        message="The request method is known by the server but is not supported by the target resource",
        code="method_not_allowed",
    )

    # 406 Not Acceptable
    not_acceptable = Error(
        message="The server cannot find any content that conforms to the criteria given by the user agent",
        code="not_acceptable",
    )

    # 409 Conflict
    conflict = Error(
        message="The request conflicts with the current state of the server",
        code="conflict",
    )

    # 422 Unprocessable Entity
    unprocessable_entity = Error(
        message="The request was well-formed but was unable to be followed due to semantic errors",
        code="unprocessable_entity",
    )

    # [5xx] HTTP response status codes
    # 500 Internal Server Error
    internal_server_error = Error(
        message="The request failed due to an internal server error",
        code="internal_server_error",
    )

    # 501 Not Implemented
    not_implemented = Error(
        message="The request is not currently supported by the server",
        code="not_implemented",
    )

    # Basic managed errors for each HTTP response status code
    basic_error_responses = {
        status.HTTP_400_BAD_REQUEST: bad_request,
        status.HTTP_401_UNAUTHORIZED: unauthorized,
        status.HTTP_403_FORBIDDEN: forbidden,
        status.HTTP_404_NOT_FOUND: not_found,
        status.HTTP_405_METHOD_NOT_ALLOWED: method_not_allowed,
        status.HTTP_406_NOT_ACCEPTABLE: not_acceptable,
        status.HTTP_409_CONFLICT: conflict,
        status.HTTP_422_UNPROCESSABLE_ENTITY: unprocessable_entity,
        status.HTTP_500_INTERNAL_SERVER_ERROR: internal_server_error,
        status.HTTP_501_NOT_IMPLEMENTED: not_implemented,
    }

    # [400] HTTP response status codes that can occur in the API's responses
    # /v1/users
    invalid_email = Error(
        message="Invalid email format",
        code="invalid_email",
    )
    duplicated_email = Error(
        message="Email already exists",
        code="duplicated_email",
    )
    invalid_username = Error(
        message="Invalid username format",
        code="invalid_username",
    )
    duplicated_username = Error(
        message="Username already exists",
        code="duplicated_username",
    )
    invalid_password = Error(
        message="Invalid password format",
        code="invalid_password",
    )

    # /v1/auth
    invalid_credentials = Error(
        message="Invalid email or password",
        code="invalid_credentials",
    )
