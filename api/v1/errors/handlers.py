from fastapi import status
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse
from fastapi.exceptions import ValidationError
from fastapi.encoders import jsonable_encoder
# from starlette.exceptions import HTTPException

from app.core.exceptions import HTTPException


async def http_error_hander(req: Request, exc: HTTPException) -> ORJSONResponse:
    return ORJSONResponse(
        content=jsonable_encoder(exc.errors),
        status_code=exc.status_code,
    )


async def http_validation_error_handler(req: Request, exc: ValidationError) -> ORJSONResponse:
    return ORJSONResponse(
        content=jsonable_encoder(exc.errors()),
        status_code=status.HTTP_400_BAD_REQUEST,
    )
