from typing import Optional, Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.permission.model import Permission


class PermissionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, permission_id: int) -> Optional[Permission]:
        result = await self.db.execute(
            select(Permission).where(
                Permission.id == permission_id, Permission.is_deleted.is_(False)
            )
        )
        return result.scalar_one_or_none()

    async def find_conflict(
        self, name: Optional[str], code: Optional[str], exclude_id: Optional[int] = None
    ) -> Optional[Permission]:
        if not name and not code:
            return None
        conditions = []
        if name:
            conditions.append(Permission.name == name)
        if code:
            conditions.append(Permission.code == code)
        stmt = select(Permission).where(or_(*conditions), Permission.is_deleted.is_(False))
        if exclude_id is not None:
            stmt = stmt.where(Permission.id != exclude_id)
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none()

    async def has_children(self, permission_id: int) -> bool:
        result = await self.db.execute(
            select(Permission.id)
            .where(Permission.parent_id == permission_id, Permission.is_deleted.is_(False))
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def add(self, permission: Permission) -> Permission:
        self.db.add(permission)
        await self.db.flush()
        await self.db.refresh(permission)
        return permission

    async def delete(self, permission: Permission) -> None:
        await self.db.delete(permission)

    async def list_permissions(
        self,
        page: int,
        page_size: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
        perm_type: Optional[str] = None,
    ) -> tuple[Sequence[Permission], int]:
        filters = [Permission.is_deleted.is_(False)]
        if name:
            filters.append(Permission.name.ilike(f"%{name}%"))
        if code:
            filters.append(Permission.code.ilike(f"%{code}%"))
        if perm_type:
            filters.append(Permission.type == perm_type)

        total = (
            await self.db.execute(select(func.count()).select_from(Permission).where(*filters))
        ).scalar_one()

        stmt = (
            select(Permission)
            .where(*filters)
            .order_by(Permission.sort_order, Permission.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return (await self.db.execute(stmt)).scalars().all(), total

    async def all_ordered(self) -> Sequence[Permission]:
        stmt = (
            select(Permission)
            .where(Permission.is_deleted.is_(False))
            .order_by(Permission.sort_order, Permission.id)
        )
        return (await self.db.execute(stmt)).scalars().all()
