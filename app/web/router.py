from fastapi import APIRouter

from app.settings.config import WEB_ENABLED
from app.web.modules.system import system_web_router
from app.web.routes.admin import router as admin_router
from app.web.routes.auth import router as auth_router
from app.web.routes.public import router as public_router

web_router = APIRouter()

if WEB_ENABLED:
    web_router.include_router(public_router)
    web_router.include_router(auth_router)
    web_router.include_router(admin_router)
    web_router.include_router(system_web_router)
