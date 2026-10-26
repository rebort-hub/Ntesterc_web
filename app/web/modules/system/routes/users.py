from typing import Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.user.model import User
from app.api.v1.system.user.schemas import UserCreate, UserUpdate
from app.api.v1.system.user.service import UserService
from app.core.database import get_db
from app.web.context import admin_page_context
from app.web.deps import require_web_user
from app.web.modules.system.menu import system_path
from app.web.render import render
from app.web.utils import humanize_error

router = APIRouter(prefix="/users", tags=["Web System Users"])


@router.get("", response_class=HTMLResponse, name="web_system_users")
async def user_list(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    users, total = await UserService(db).list_users(
        page=page,
        page_size=page_size,
        username=username or None,
        email=email or None,
    )
    ctx = await admin_page_context(
        request,
        current_user,
        active_nav="users",
        title="用户管理",
        db=db,
        users=users,
        total=total,
        page=page,
        page_size=page_size,
        username_filter=username or "",
        email_filter=email or "",
        list_url=system_path("/users"),
    )
    return render(request, "modules/system/users/list.html", ctx)


@router.get("/create", response_class=HTMLResponse, name="web_system_users_create")
async def user_create_form(
    request: Request,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    ctx = await admin_page_context(
        request,
        current_user,
        active_nav="users",
        title="新建用户",
        db=db,
        form_action=system_path("/users/create"),
        user_obj=None,
        error=None,
    )
    return render(request, "modules/system/users/form.html", ctx)


@router.post("/create", response_class=HTMLResponse)
async def user_create_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    is_active: Optional[str] = Form(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    active = is_active in ("on", "true", "1", "yes")
    try:
        await UserService(db).create_user(
            UserCreate(username=username.strip(), email=email.strip(), password=password, is_active=active)
        )
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/users')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/users')}?ok=created", status_code=302)


@router.get("/{user_id}/edit", response_class=HTMLResponse, name="web_system_users_edit")
async def user_edit_form(
    request: Request,
    user_id: int,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        user_obj = await UserService(db).get_user(user_id)
    except ValueError:
        return RedirectResponse(f"{system_path('/users')}?err=用户不存在", status_code=302)
    ctx = await admin_page_context(
        request,
        current_user,
        active_nav="users",
        title="编辑用户",
        db=db,
        form_action=system_path(f"/users/{user_id}/edit"),
        user_obj=user_obj,
        error=None,
    )
    return render(request, "modules/system/users/form.html", ctx)


@router.post("/{user_id}/edit", response_class=HTMLResponse)
async def user_edit_submit(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(""),
    is_active: Optional[str] = Form(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    active = is_active in ("on", "true", "1", "yes")
    payload = UserUpdate(username=username.strip(), email=email.strip(), is_active=active)
    if password.strip():
        payload.password = password
    try:
        await UserService(db).update_user(user_id, payload)
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/users')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/users')}?ok=updated", status_code=302)


@router.post("/{user_id}/delete", name="web_system_users_delete")
async def user_delete(
    user_id: int,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    if not current_user.is_superadmin:
        return RedirectResponse(f"{system_path('/users')}?err=需要超级管理员权限", status_code=302)
    try:
        await UserService(db).delete_user(user_id)
    except ValueError as e:
        return RedirectResponse(
            f"{system_path('/users')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/users')}?ok=deleted", status_code=302)
