from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.api_v1.api import router


def get_application() -> FastAPI:

    application = FastAPI()

    application.include_router(router, prefix="/v1")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return application


app = get_application()
handler = Mangum(app)
