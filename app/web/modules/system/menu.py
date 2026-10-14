from app.settings.config import WEB_ADMIN_PREFIX

_SYSTEM_PREFIX = f"{WEB_ADMIN_PREFIX}/system"


def system_path(segment: str) -> str:
    segment = segment if segment.startswith("/") else f"/{segment}"
    return f"{_SYSTEM_PREFIX}{segment}"


SYSTEM_MENUS = [
    {
        "code": "users",
        "name": "用户管理",
        "path": system_path("/users"),
        "api_prefix": "/api/v1/system/users",
        "icon": "user",
    },
    {
        "code": "roles",
        "name": "角色管理",
        "path": system_path("/roles"),
        "api_prefix": "/api/v1/system/roles",
        "icon": "team",
    },
    {
        "code": "permissions",
        "name": "权限管理",
        "path": system_path("/permissions"),
        "api_prefix": "/api/v1/system/permissions",
        "icon": "safety",
    },
]

WEB_MENU_GROUPS = [
    {
        "code": "system",
        "name": "系统管理",
        "icon": "setting",
        "children": SYSTEM_MENUS,
    },
]
