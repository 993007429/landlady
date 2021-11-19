from fastapi import APIRouter

from app.api.routers import box, project

router = APIRouter()
router.include_router(box.router)
router.include_router(project.router)
