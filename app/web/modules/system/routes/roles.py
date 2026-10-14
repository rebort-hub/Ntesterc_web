from typing import Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.role.schemas import RoleCreate, RoleUpdate
from app.api.v1.system.role.service import RoleService
from app.api.v1.system.user.model import User
from app.core.database import get_db
from app.web.context import admin_page_context
from app.web.deps import require_web_user
from app.web.modules.system.menu import system_path
from app.web.render import render
from app.web.utils import humanize_error

router = APIRouter(prefix="/roles", tags=["Web System Roles"])


@router.get("", response_class=HTMLResponse, name="web_system_roles")
async def role_list(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    roles, total = await RoleService(db).list_roles(page, page_size, name, code)
    ctx = admin_page_context(
        request,
        current_user,
        active_nav="roles",
        title="角色管理",
        roles=roles,
        total=total,
        page=page,
        page_size=page_size,
        name_filter=name or "",
        code_filter=code or "",
        list_url=system_path("/roles"),
    )
    return render(request, "modules/system/roles/list.html", ctx)


@router.get("/create", response_class=HTMLResponse, name="web_system_roles_create")
async def role_create_form(
    request: Request,
    current_user: User = Depends(require_web_user),
):
    ctx = admin_page_context(
        request,
        current_user,
        active_nav="roles",
        title="新建角色",
        form_action=system_path("/roles/create"),
        role_obj=None,
        error=None,
    )
    return render(request, "modules/system/roles/form.html", ctx)


@router.post("/create", response_class=HTMLResponse)
async def role_create_submit(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    description: str = Form(""),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await RoleService(db).create_role(
            RoleCreate(name=name.strip(), code=code.strip(), description=description.strip() or None)
        )
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/roles')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/roles')}?ok=created", status_code=302)


@router.get("/{role_id}/edit", response_class=HTMLResponse, name="web_system_roles_edit")
async def role_edit_form(
    request: Request,
    role_id: int,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    role_obj = await RoleService(db).get_role(role_id)
    if not role_obj:
        return RedirectResponse(f"{system_path('/roles')}?err=角色不存在", status_code=302)
    ctx = admin_page_context(
        request,
        current_user,
        active_nav="roles",
        title="编辑角色",
        form_action=system_path(f"/roles/{role_id}/edit"),
        role_obj=role_obj,
        error=None,
    )
    return render(request, "modules/system/roles/form.html", ctx)


@router.post("/{role_id}/edit", response_class=HTMLResponse)
async def role_edit_submit(
    request: Request,
    role_id: int,
    name: str = Form(...),
    code: str = Form(...),
    description: str = Form(""),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await RoleService(db).update_role(
            role_id,
            RoleUpdate(
                name=name.strip(),
                code=code.strip(),
                description=description.strip() or None,
            ),
        )
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/roles')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/roles')}?ok=updated", status_code=302)


@router.post("/{role_id}/delete", name="web_system_roles_delete")
async def role_delete(
    role_id: int,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    role_obj = await RoleService(db).get_role(role_id)
    if role_obj and role_obj.is_system:
        return RedirectResponse(f"{system_path('/roles')}?err=系统内置角色不可删除", status_code=302)
    try:
        await RoleService(db).delete_role(role_id)
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/roles')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/roles')}?ok=deleted", status_code=302)
