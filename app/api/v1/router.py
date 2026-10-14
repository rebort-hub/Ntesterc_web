from fastapi import APIRouter
from app.api.v1.system import system_router
from app.api.v1.system.auth.controller import router as auth_router
from app.api.v1.system.permission.controller import router as permission_router
from app.api.v1.system.role.controller import router as role_router
from app.api.v1.system.user.controller import router as user_router
from app.core.discover import get_plugin_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(system_router)
api_v1_router.include_router(get_plugin_router())

legacy_api_router = APIRouter(prefix="/api")
legacy_api_router.include_router(auth_router, prefix="/auth", tags=["认证"], include_in_schema=False)
legacy_api_router.include_router(user_router, prefix="/users", tags=["用户管理"], include_in_schema=False)
legacy_api_router.include_router(role_router, prefix="/roles", tags=["角色管理"], include_in_schema=False)
legacy_api_router.include_router(
    permission_router, prefix="/permissions", tags=["权限管理"], include_in_schema=False
)

api_router = APIRouter()
api_router.include_router(api_v1_router)
api_router.include_router(legacy_api_router)
