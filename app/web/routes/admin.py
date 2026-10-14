from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from app.api.v1.system.user.model import User
from app.settings.config import WEB_ADMIN_PREFIX
from app.web.context import admin_page_context
from app.web.deps import require_web_user
from app.web.modules.system.menu import system_path
from app.web.render import render

router = APIRouter(prefix=WEB_ADMIN_PREFIX, tags=["Web Admin"])


@router.get("", response_class=HTMLResponse, name="web_admin_dashboard")
async def admin_dashboard(
    request: Request,
    current_user: User = Depends(require_web_user),
):
    ctx = admin_page_context(
        request,
        current_user,
        active_nav="dashboard",
        active_module="",
        title="控制台",
        system_users_path=system_path("/users"),
    )
    return render(request, "admin/dashboard.html", ctx)
