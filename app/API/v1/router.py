from fastapi import APIRouter
from ..v1.modules.assistance.routes import router as assistance_router
from ..v1.modules.assistance_construction.routes import router as assistance_construction_router

router = APIRouter()


router.include_router(assistance_router)
router.include_router(assistance_construction_router)
