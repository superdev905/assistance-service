from fastapi import APIRouter
from ..v1.modules.assistance.routes import router as assistance_router

router = APIRouter()


router.include_router(assistance_router)