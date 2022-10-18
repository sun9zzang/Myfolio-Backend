from fastapi import APIRouter

from app.api_v1.routes import login, register

router = APIRouter()

router.include_router(login.router, prefix="/login")
router.include_router(register.router, prefix="/register")
