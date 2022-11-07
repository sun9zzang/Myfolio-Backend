from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse
# from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.api_v1.api import router
from app.api_v1.errors.handlers import http_error_hander, http_validation_error_handler


def get_application() -> FastAPI:

    application = FastAPI(default_response_class=JSONResponse)

    application.include_router(router, prefix="/v1")

    # application.add_middleware(
    #     CORSMiddleware,
    #     allow_origins=["*"],
    #     allow_credentials=True,
    #     allow_methods=["*"],
    #     allow_headers=["*"],
    # )
    application.add_exception_handler(HTTPException, http_error_hander)
    application.add_exception_handler(RequestValidationError, http_validation_error_handler)

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
        "Access-Control-Allow-Headers": "*"
    }
    if "headers" in response:
        response["headers"].update(cors_headers)
    else:
        response["headers"] = cors_headers

    print("# RESPONSE(after_append_header)")
    print(response)
    return response
