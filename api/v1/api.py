from fastapi import APIRouter

from api.v1.routes import auth
from api.v1.routes import users

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users", tags=["Users"])
