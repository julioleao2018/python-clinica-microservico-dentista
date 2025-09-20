from fastapi import APIRouter
from .routes import usuarios_routes

router = APIRouter()

# router.include_router(auth_routes.router)
# router.include_router(contratos_routes.router)
router.include_router(usuarios_routes.router)