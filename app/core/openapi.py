from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi_schema(app: FastAPI) -> dict:
    schema = get_openapi(
        title="Myfolio API",
        version="0.1.0",
        description="Myfolio API 문서입니다.",
        routes=app.routes,
    )

    return schema
