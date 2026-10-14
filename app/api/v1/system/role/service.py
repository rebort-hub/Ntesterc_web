from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.role.model import Role
from app.api.v1.system.role.repository import RoleRepository
from app.api.v1.system.role.schemas import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RoleRepository(db)

    async def create_role(self, role_data: RoleCreate) -> Role:
        conflict = await self.repo.find_conflict(role_data.name, role_data.code)
        if conflict:
            if conflict.name == role_data.name:
                raise ValueError("role name exists")
            raise ValueError("role code exists")
        return await self.repo.add(Role(**role_data.model_dump()))

    async def update_role(self, role_id: int, role_data: RoleUpdate) -> Role:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise ValueError("role not found")
        update_data = role_data.model_dump(exclude_unset=True)
        if update_data:
            conflict = await self.repo.find_conflict(
                update_data.get("name"),
                update_data.get("code"),
                exclude_id=role_id,
            )
            if conflict:
                if "name" in update_data and conflict.name == update_data["name"]:
                    raise ValueError("role name exists")
                if "code" in update_data and conflict.code == update_data["code"]:
                    raise ValueError("role code exists")
            for field, value in update_data.items():
                setattr(role, field, value)
            await self.db.flush()
            await self.db.refresh(role)
        return role

    async def delete_role(self, role_id: int) -> None:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise ValueError("role not found")
        await self.repo.delete(role)

    async def get_role(self, role_id: int) -> Optional[Role]:
        return await self.repo.get_by_id(role_id)

    async def list_roles(
        self,
        page: int = 1,
        page_size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
    ) -> tuple[Sequence[Role], int]:
        return await self.repo.list_roles(page, page_size, name, code)
