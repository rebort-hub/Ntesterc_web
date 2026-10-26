from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.settings.config import WEB_ADMIN_PREFIX
from app.core.icons import normalize_icon

_SYSTEM_PREFIX = f"{WEB_ADMIN_PREFIX}/system"


def system_path(segment: str) -> str:
    segment = segment if segment.startswith("/") else f"/{segment}"
    return f"{_SYSTEM_PREFIX}{segment}"


# 静态兜底（库中无目录/菜单时使用）
SYSTEM_MENUS = [
    {
        "code": "users",
        "name": "用户管理",
        "path": system_path("/users"),
        "icon": "layui-icon-user",
    },
    {
        "code": "roles",
        "name": "角色管理",
        "path": system_path("/roles"),
        "icon": "layui-icon-group",
    },
    {
        "code": "permissions",
        "name": "权限管理",
        "path": system_path("/permissions"),
        "icon": "layui-icon-vercode",
    },
]

WEB_MENU_GROUPS = [
    {
        "code": "system",
        "name": "系统管理",
        "icon": "layui-icon-set",
        "children": SYSTEM_MENUS,
    },
]


def _nav_code(path: str | None, code: str) -> str:
    if path:
        seg = path.rstrip("/").split("/")[-1]
        if seg:
            return seg
    parts = (code or "").replace(":", ".").split(".")
    for part in reversed(parts):
        if part and part not in ("menu", "system", "api"):
            return part
    return code or "item"


def _group_code(code: str) -> str:
    parts = (code or "").replace(":", ".").split(".")
    return parts[0] if parts and parts[0] else "group"


def _menu_item_from_node(node: Any) -> dict[str, Any]:
    return {
        "code": _nav_code(getattr(node, "path", None), getattr(node, "code", "")),
        "name": node.name,
        "path": node.path or "#",
        "icon": normalize_icon(getattr(node, "icon", None), default="layui-icon-circle-dot"),
        "open_type": getattr(node, "open_type", None) or "_self",
        "perm_code": node.code,
    }


def _is_enabled(node: Any) -> bool:
    return bool(getattr(node, "is_enabled", True))


def _collect_menus(node: Any) -> list[dict[str, Any]]:
    """递归收集某节点下已启用的 menu（含子目录）；禁用目录整支跳过。"""
    items: list[dict[str, Any]] = []
    for child in getattr(node, "children", None) or []:
        if not _is_enabled(child):
            continue
        if child.type == "menu" and child.path:
            items.append(_menu_item_from_node(child))
        elif child.type == "directory":
            items.extend(_collect_menus(child))
    return items


async def build_web_menu_groups(db: AsyncSession) -> list[dict[str, Any]]:
    """从权限树构建侧栏：directory=分组，menu=叶子；禁用项不出现在侧栏。"""
    from app.api.v1.system.permission.service import PermissionService

    tree = await PermissionService(db).get_permission_tree()
    groups: list[dict[str, Any]] = []

    for node in tree:
        if not _is_enabled(node):
            continue
        if node.type == "directory":
            children = _collect_menus(node)
            if not children:
                continue
            groups.append(
                {
                    "code": _group_code(node.code),
                    "name": node.name,
                    "icon": normalize_icon(node.icon, default="layui-icon-set"),
                    "children": children,
                    "perm_code": node.code,
                }
            )
        elif node.type == "menu" and node.path:
            groups.append(
                {
                    "code": _nav_code(node.path, node.code),
                    "name": node.name,
                    "icon": normalize_icon(node.icon, default="layui-icon-file"),
                    "children": [_menu_item_from_node(node)],
                    "perm_code": node.code,
                }
            )

    return groups if groups else list(WEB_MENU_GROUPS)
