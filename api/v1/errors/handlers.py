from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse

from app.core.strings import ErrorTypes


def http_error_hander(req: Request, exc: HTTPException) -> ORJSONResponse:
    content = {
        "type": ErrorTypes.invalid_request_error.value,
        "detail": exc.detail,
    }

    return ORJSONResponse(
        content,
        status_code=exc.status_code,
    )


def http_validation_error_handler(req: Request, exc: RequestValidationError) -> ORJSONResponse:
    content = {
        "type": ErrorTypes.invalid_request_error.value,
        "detail": exc.json(),
    }

    return ORJSONResponse(
        content,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
