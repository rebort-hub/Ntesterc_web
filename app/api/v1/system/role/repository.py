from typing import Optional, Sequence
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.system.role.model import Role


class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, role_id: int) -> Optional[Role]:
        result = await self.db.execute(
            select(Role).where(Role.id == role_id, Role.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def find_conflict(
        self, name: Optional[str], code: Optional[str], exclude_id: Optional[int] = None
    ) -> Optional[Role]:
        if not name and not code:
            return None
        conditions = []
        if name:
            conditions.append(Role.name == name)
        if code:
            conditions.append(Role.code == code)
        stmt = select(Role).where(or_(*conditions), Role.is_deleted.is_(False))
        if exclude_id is not None:
            stmt = stmt.where(Role.id != exclude_id)
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none()

    async def add(self, role: Role) -> Role:
        self.db.add(role)
        await self.db.flush()
        await self.db.refresh(role)
        return role

    async def delete(self, role: Role) -> None:
        await self.db.delete(role)

    async def list_roles(
        self,
        page: int,
        page_size: int,
        name: Optional[str] = None,
        code: Optional[str] = None,
    ) -> tuple[Sequence[Role], int]:
        filters = [Role.is_deleted.is_(False)]
        if name:
            filters.append(Role.name.ilike(f"%{name}%"))
        if code:
            filters.append(Role.code.ilike(f"%{code}%"))

        total = (
            await self.db.execute(select(func.count()).select_from(Role).where(*filters))
        ).scalar_one()

        stmt = (
            select(Role)
            .where(*filters)
            .order_by(Role.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return (await self.db.execute(stmt)).scalars().all(), total
