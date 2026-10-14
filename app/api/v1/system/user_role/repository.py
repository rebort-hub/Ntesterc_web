from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.permission.model import Permission
from app.api.v1.system.role.model import Role, role_permission
from app.api.v1.system.user_role.model import UserRole


class UserRoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_role_codes_for_user(self, user_id: int) -> set[str]:
        stmt = (
            select(Role.code)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, Role.is_deleted.is_(False))
        )
        return set((await self.db.execute(stmt)).scalars().all())

    async def get_permission_codes_for_user(self, user_id: int) -> set[str]:
        stmt = (
            select(Permission.code)
            .join(role_permission, role_permission.c.permission_id == Permission.id)
            .join(Role, Role.id == role_permission.c.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                Permission.is_deleted.is_(False),
                Role.is_deleted.is_(False),
            )
            .distinct()
        )
        return set((await self.db.execute(stmt)).scalars().all())
