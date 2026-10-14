from fastapi import APIRouter
from app.api.v1.system.auth.controller import router as AuthRouter
from app.api.v1.system.permission.controller import router as PermissionRouter
from app.api.v1.system.role.controller import router as RoleRouter
from app.api.v1.system.user.controller import router as UserRouter

system_router = APIRouter(prefix="/system")

system_router.include_router(AuthRouter, prefix="/auth", tags=["认证"])
system_router.include_router(UserRouter, prefix="/users", tags=["用户管理"])
system_router.include_router(RoleRouter, prefix="/roles", tags=["角色管理"])
system_router.include_router(PermissionRouter, prefix="/permissions", tags=["权限管理"])
