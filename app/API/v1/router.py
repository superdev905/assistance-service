from fastapi import APIRouter
from ..v1.modules.visit.routes import router as visit_router
from ..v1.modules.assistance.routes import router as assistance_router
from ..v1.modules.assistance_construction.routes import router as assistance_construction_router
from ..v1.modules.attachment.routes import router as attachment_router
from ..v1.modules.report_item.routes import router as report_item_router


router = APIRouter()


router.include_router(visit_router)
router.include_router(assistance_router)
router.include_router(assistance_construction_router)
router.include_router(attachment_router)
router.include_router(report_item_router)
