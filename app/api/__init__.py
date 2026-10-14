from fastapi import APIRouter

from app.api.v1.router import api_router
from app.api.views import view_router

router = APIRouter()
router.include_router(api_router)
router.include_router(view_router)
