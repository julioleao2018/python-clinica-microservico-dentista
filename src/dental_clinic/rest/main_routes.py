from fastapi import APIRouter
from .routes import usuarios, registro

router = APIRouter()

router.include_router(usuarios.router)
router.include_router(registro.router)