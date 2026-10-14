from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.auth.service import AuthService
from app.api.v1.system.user.model import User
from app.core.database import get_db
from app.core.exceptions.auth import InvalidCredentialsError
from app.settings.config import WEB_LOGIN_PATH, WEB_LOGIN_REDIRECT
from app.web.cookies import clear_auth_cookies, set_auth_cookies
from app.web.deps import get_optional_web_user
from app.web.render import render

router = APIRouter(tags=["Web"])


@router.get(WEB_LOGIN_PATH, response_class=HTMLResponse, name="web_login")
async def login_page(
    request: Request,
    current_user: User | None = Depends(get_optional_web_user),
):
    if current_user is not None:
        return RedirectResponse(url=WEB_LOGIN_REDIRECT, status_code=302)
    return render(
        request,
        "auth/login.html",
        {"title": "登录", "error": None},
    )


@router.post(WEB_LOGIN_PATH, response_class=HTMLResponse, name="web_login_submit")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    try:
        tokens = await service.login(username.strip(), password)
    except InvalidCredentialsError:
        return render(
            request,
            "auth/login.html",
            {"title": "登录", "error": "用户名或密码错误"},
            status_code=400,
        )

    response = RedirectResponse(url=WEB_LOGIN_REDIRECT, status_code=302)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return response


@router.get("/logout", name="web_logout")
async def logout():
    response = RedirectResponse(url=WEB_LOGIN_PATH, status_code=302)
    clear_auth_cookies(response)
    return response
