from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from mangum import Mangum

from api.v1.api import router
from app.core.errors.handlers import (
    http_exception_hander,
    request_validation_exception_handler,
    starlette_http_exception_handler,
)
from app.core.openapi import custom_openapi
from app.core.exceptions import HTTPException


def get_application() -> FastAPI:

    application = FastAPI(default_response_class=ORJSONResponse)

    application.include_router(router, prefix="/v1")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_exception_handler(HTTPException, http_exception_hander)
    application.add_exception_handler(
        StarletteHTTPException, starlette_http_exception_handler
    )
    application.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )

    application.openapi_schema = custom_openapi(application)

    return application


app = get_application()


def handler(event, context):
    print("# EVENT")
    print(event)
    print("# CONTEXT")
    print(context)

    asgi_handler = Mangum(app)
    print("# ASGI_HANDLER")
    print(asgi_handler)

    response = asgi_handler(event, context)
    print("# RESPONSE")
    print(response)

    return response
