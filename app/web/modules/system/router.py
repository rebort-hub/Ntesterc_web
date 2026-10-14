from fastapi import APIRouter

from app.settings.config import WEB_ADMIN_PREFIX
from app.web.modules.system.routes.permissions import router as permissions_router
from app.web.modules.system.routes.roles import router as roles_router
from app.web.modules.system.routes.users import router as users_router

system_web_router = APIRouter(prefix=f"{WEB_ADMIN_PREFIX}/system", tags=["Web System"])

system_web_router.include_router(users_router)
system_web_router.include_router(roles_router)
system_web_router.include_router(permissions_router)
