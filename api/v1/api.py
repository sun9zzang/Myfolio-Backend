from fastapi import APIRouter

from api.v1.routes import auth, templates, users, folios

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(
    templates.router, prefix="/templates", tags=["Templates"]
)
router.include_router(folios.router, prefix="/folios", tags=["Folios"])
