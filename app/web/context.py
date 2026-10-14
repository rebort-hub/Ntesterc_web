from typing import Any, Optional

from fastapi import Request

from app.api.v1.system.user.model import User
from app.web.modules.system.menu import WEB_MENU_GROUPS


def parse_flash(request: Request) -> tuple[Optional[str], Optional[str]]:
    return request.query_params.get("ok"), request.query_params.get("err")


FLASH_MESSAGES = {
    "created": "创建成功",
    "updated": "保存成功",
    "deleted": "删除成功",
}


def admin_page_context(
    request: Request,
    current_user: User,
    *,
    active_nav: str,
    active_module: str = "system",
    title: str,
    **extra: Any,
) -> dict[str, Any]:
    ok_key, err_msg = parse_flash(request)
    flash_ok = FLASH_MESSAGES.get(ok_key) if ok_key else None
    return {
        "title": title,
        "current_user": current_user,
        "active_nav": active_nav,
        "active_module": active_module,
        "web_menu_groups": WEB_MENU_GROUPS,
        "flash_ok": flash_ok,
        "flash_err": err_msg,
        **extra,
    }
