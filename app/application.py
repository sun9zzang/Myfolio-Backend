from fastapi import FastAPI
from fastapi.exceptions import ValidationError, RequestValidationError
from fastapi.responses import ORJSONResponse
# from starlette.exceptions import HTTPException

from mangum import Mangum

from api.v1.api import router
from api.v1.errors.handlers import http_error_hander, http_validation_error_handler
from app.core.openapi import custom_openapi_schema
from app.core.exceptions import HTTPException


def get_application() -> FastAPI:

    application = FastAPI(default_response_class=ORJSONResponse)

    application.include_router(router, prefix="/v1")

    application.add_exception_handler(HTTPException, http_error_hander)
    application.add_exception_handler(ValidationError, http_validation_error_handler)
    application.add_exception_handler(
        RequestValidationError, http_validation_error_handler
    )

    application.openapi_schema = custom_openapi_schema(application)

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

    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Credentials": True,
        "Access-Control-Allow-Methods": "*",
        "Access-Control-Allow-Headers": "*",
    }
    if "headers" in response:
        response["headers"].update(cors_headers)
    else:
        response["headers"] = cors_headers

    print("# RESPONSE(after_append_header)")
    print(response)
    return response
