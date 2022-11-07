from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.core.strings import ErrorTypes


def http_error_hander(req: Request, exc: HTTPException) -> JSONResponse:
    content = {
        "type": ErrorTypes.invalid_request_error.value,
        "detail": exc.detail,
    }

    return JSONResponse(
        content,
        status_code=exc.status_code,
    )


def http_validation_error_handler(req: Request, exc: RequestValidationError) -> JSONResponse:
    content = {
        "type": ErrorTypes.invalid_request_error.value,
        "detail": exc.json(),
    }

    return JSONResponse(
        content,
        status_code=status.HTTP_400_BAD_REQUEST,
    )
