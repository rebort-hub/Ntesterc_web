from typing import Any, Mapping, Optional

from fastapi import Request
from starlette.responses import Response

from app.core.events.templates import templates
from app.settings.config import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    WEB_ADMIN_PREFIX,
    WEB_LOGIN_PATH,
)


def base_context(request: Request, **extra: Any) -> dict[str, Any]:
    ctx: dict[str, Any] = {
        "request": request,
        "app_name": APP_NAME,
        "app_description": APP_DESCRIPTION,
        "app_version": APP_VERSION,
        "web_login_path": WEB_LOGIN_PATH,
        "web_admin_prefix": WEB_ADMIN_PREFIX,
        "static_logo": "web/logo.png",
        "static_login_bg": "web/background.png",
        "login_product_title": APP_NAME,
    }
    ctx.update(extra)
    return ctx


def render(
    request: Request,
    template: str,
    context: Optional[Mapping[str, Any]] = None,
    status_code: int = 200,
) -> Response:
    merged = base_context(request, **(dict(context) if context else {}))
    return templates.TemplateResponse(template, merged, status_code=status_code)
