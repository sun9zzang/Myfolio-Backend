from fastapi import APIRouter

from app.api_v1.routes import auth, users

router = APIRouter()

router.include_router(auth.router, prefix="/auth")
router.include_router(users.router, prefix="/users")
