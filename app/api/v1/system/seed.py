import json
import os
from typing import Any
from sqlalchemy import func, insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.system.permission.model import Permission
from app.api.v1.system.role.model import Role, role_permission
from app.api.v1.system.user.model import User
from app.api.v1.system.user_role.model import UserRole
from app.config.path_conf import SEED_DATA_DIR
from app.core.database import async_session_factory
from app.log.config.log_config import get_logger

logger = get_logger(__name__)

SEED_ORDER = ("roles", "permissions", "users", "user_roles")


async def seed_system_data() -> None:
    async with async_session_factory() as session:
        async with session.begin():
            await _seed_all(session)


async def _seed_all(db: AsyncSession) -> None:
    role_map: dict[str, Role] = {}
    user_map: dict[str, User] = {}

    for table in SEED_ORDER:
        rows = _load_json(table)
        if not rows:
            continue

        model = {
            "roles": Role,
            "permissions": Permission,
            "users": User,
            "user_roles": UserRole,
        }[table]
        count = (await db.execute(select(func.count()).select_from(model))).scalar_one()
        if count and count > 0:
            logger.info("skip seed %s (%s rows)", table, count)
            continue

        if table == "roles":
            for item in rows:
                role = Role(**item)
                db.add(role)
                role_map[role.code] = role
            await db.flush()

        elif table == "permissions":
            pending_parents: list[tuple[Permission, str]] = []
            for item in rows:
                raw = dict(item)
                parent_code = raw.pop("parent_code", None)
                perm = Permission(**raw)
                db.add(perm)
                if parent_code:
                    pending_parents.append((perm, parent_code))
            await db.flush()
            if pending_parents:
                code_map = {
                    p.code: p
                    for p in (await db.execute(select(Permission))).scalars().all()
                }
                for perm, parent_code in pending_parents:
                    parent = code_map.get(parent_code)
                    if parent:
                        perm.parent_id = parent.id
                await db.flush()
            admin_role = await _get_role_by_code(db, "admin")
            if admin_role:
                perms = (await db.execute(select(Permission))).scalars().all()
                for perm in perms:
                    await db.execute(
                        insert(role_permission).values(
                            role_id=admin_role.id, permission_id=perm.id
                        )
                    )

        elif table == "users":
            for item in rows:
                raw = dict(item)
                password = raw.pop("password", None)
                user = User(**raw)
                user.set_password(password or "admin123")
                db.add(user)
                user_map[user.username] = user
            await db.flush()

        elif table == "user_roles":
            for item in rows:
                user = user_map.get(item["username"]) or await _get_user_by_name(
                    db, item["username"]
                )
                role = role_map.get(item["role_code"]) or await _get_role_by_code(
                    db, item["role_code"]
                )
                if not user or not role:
                    continue
                db.add(
                    UserRole(
                        user_id=user.id,
                        role_id=role.id,
                        data_scope=item.get("data_scope", "all"),
                    )
                )
            await db.flush()


async def _get_role_by_code(db: AsyncSession, code: str) -> Role | None:
    result = await db.execute(select(Role).where(Role.code == code))
    return result.scalar_one_or_none()


async def _get_user_by_name(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


def _load_json(name: str) -> list[dict[str, Any]]:
    path = os.path.join(SEED_DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as file:
        return json.load(file)
