from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from app.api.v1.system.user.model import User
from app.settings.config import WEB_ADMIN_PREFIX, WEB_LOGIN_REDIRECT
from app.web.deps import get_optional_web_user
from app.web.render import render

router = APIRouter(tags=["Web"])


@router.get("/", response_class=HTMLResponse, name="web_home")
async def home(
    request: Request,
    current_user: User | None = Depends(get_optional_web_user),
):
    if current_user is not None:
        return RedirectResponse(url=WEB_LOGIN_REDIRECT, status_code=302)
    return render(
        request,
        "public/index.html",
        {
            "title": "首页",
            "current_user": None,
        },
    )
