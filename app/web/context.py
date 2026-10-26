from typing import Any, Optional

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.user.model import User
from app.web.modules.system.menu import WEB_MENU_GROUPS, build_web_menu_groups


def parse_flash(request: Request) -> tuple[Optional[str], Optional[str]]:
    return request.query_params.get("ok"), request.query_params.get("err")


FLASH_MESSAGES = {
    "created": "创建成功",
    "updated": "保存成功",
    "deleted": "删除成功",
}


async def admin_page_context(
    request: Request,
    current_user: User,
    *,
    active_nav: str,
    active_module: str = "system",
    title: str,
    db: AsyncSession | None = None,
    **extra: Any,
) -> dict[str, Any]:
    ok_key, err_msg = parse_flash(request)
    flash_ok = FLASH_MESSAGES.get(ok_key) if ok_key else None

    menu_groups = extra.pop("web_menu_groups", None)
    if menu_groups is None:
        if db is not None:
            try:
                menu_groups = await build_web_menu_groups(db)
            except Exception:
                menu_groups = WEB_MENU_GROUPS
        else:
            menu_groups = WEB_MENU_GROUPS

    # 根据当前 path 推断 active_module / active_nav（权限改名后仍能高亮）
    path = request.url.path.rstrip("/")
    inferred_module = active_module
    inferred_nav = active_nav
    for group in menu_groups:
        for item in group.get("children") or []:
            item_path = (item.get("path") or "").rstrip("/")
            if item_path and path == item_path:
                inferred_module = group.get("code") or inferred_module
                inferred_nav = item.get("code") or inferred_nav
                break

    return {
        "title": title,
        "current_user": current_user,
        "active_nav": inferred_nav,
        "active_module": inferred_module,
        "web_menu_groups": menu_groups,
        "flash_ok": flash_ok,
        "flash_err": err_msg,
        **extra,
    }
