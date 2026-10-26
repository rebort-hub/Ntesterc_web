from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.system.permission.model import PERMISSION_TYPES, Permission
from app.api.v1.system.permission.repository import PermissionRepository
from app.api.v1.system.permission.schemas import (
    PermissionCreate,
    PermissionTreeNode,
    PermissionUpdate,
)


class PermissionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = PermissionRepository(db)

    async def create_permission(self, permission_data: PermissionCreate) -> Permission:
        conflict = await self.repo.find_conflict(permission_data.name, permission_data.code)
        if conflict:
            if conflict.name == permission_data.name:
                raise ValueError("permission name exists")
            raise ValueError("permission code exists")
        if permission_data.type not in PERMISSION_TYPES:
            raise ValueError(f"invalid permission type: {list(PERMISSION_TYPES)}")
        if permission_data.parent_id:
            parent = await self.repo.get_by_id(permission_data.parent_id)
            if not parent:
                raise ValueError("parent permission not found")
        return await self.repo.add(Permission(**permission_data.model_dump()))

    async def update_permission(
        self, permission_id: int, permission_data: PermissionUpdate
    ) -> Permission:
        permission = await self.repo.get_by_id(permission_id)
        if not permission:
            raise ValueError("permission not found")
        update_data = permission_data.model_dump(exclude_unset=True)
        if not update_data:
            return permission
        conflict = await self.repo.find_conflict(
            update_data.get("name"),
            update_data.get("code"),
            exclude_id=permission_id,
        )
        if conflict:
            if "name" in update_data and conflict.name == update_data["name"]:
                raise ValueError("permission name exists")
            if "code" in update_data and conflict.code == update_data["code"]:
                raise ValueError("permission code exists")
        if "type" in update_data and update_data["type"] not in PERMISSION_TYPES:
            raise ValueError(f"invalid permission type: {list(PERMISSION_TYPES)}")
        if "parent_id" in update_data:
            if update_data["parent_id"] == permission_id:
                raise ValueError("cannot set self as parent")
            if update_data["parent_id"]:
                parent = await self.repo.get_by_id(update_data["parent_id"])
                if not parent:
                    raise ValueError("parent permission not found")
        for field, value in update_data.items():
            setattr(permission, field, value)
        await self.db.flush()
        await self.db.refresh(permission)
        return permission

    async def set_enabled(self, permission_id: int, enabled: bool) -> Permission:
        return await self.update_permission(
            permission_id, PermissionUpdate(is_enabled=bool(enabled))
        )

    async def delete_permission(self, permission_id: int) -> None:
        permission = await self.repo.get_by_id(permission_id)
        if not permission:
            raise ValueError("permission not found")
        if await self.repo.has_children(permission_id):
            raise ValueError("permission has children")
        await self.repo.delete(permission)

    async def get_permission(self, permission_id: int) -> Permission:
        permission = await self.repo.get_by_id(permission_id)
        if not permission:
            raise ValueError("permission not found")
        return permission

    async def list_permissions(
        self,
        page: int = 1,
        page_size: int = 10,
        name: Optional[str] = None,
        code: Optional[str] = None,
        perm_type: Optional[str] = None,
    ) -> tuple[Sequence[Permission], int]:
        if perm_type and perm_type not in PERMISSION_TYPES:
            raise ValueError(f"invalid permission type: {list(PERMISSION_TYPES)}")
        return await self.repo.list_permissions(page, page_size, name, code, perm_type)

    async def get_permission_tree(self) -> list[PermissionTreeNode]:
        permissions = await self.repo.all_ordered()
        permission_dict = {
            p.id: PermissionTreeNode(
                id=p.id,
                name=p.name,
                code=p.code,
                description=p.description,
                type=p.type,
                path=p.path,
                icon=getattr(p, "icon", None),
                open_type=getattr(p, "open_type", None),
                is_enabled=bool(getattr(p, "is_enabled", True)),
                parent_id=p.parent_id,
                sort_order=p.sort_order,
                children=[],
            )
            for p in permissions
        }
        roots: list[PermissionTreeNode] = []
        for node in permission_dict.values():
            if node.parent_id is None:
                roots.append(node)
            else:
                parent = permission_dict.get(node.parent_id)
                if parent:
                    parent.children.append(node)
        return roots
