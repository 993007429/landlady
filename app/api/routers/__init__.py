from fastapi import APIRouter

from app.api.routers import box

router = APIRouter()

router.include_router(box.router, prefix="/box")
