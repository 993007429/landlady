from fastapi import APIRouter

from app.api.routers import box, uat

router = APIRouter()
router.include_router(box.router)
router.include_router(uat.router)
