from typing import Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.permission.model import PERMISSION_TYPES
from app.api.v1.system.permission.schemas import PermissionCreate, PermissionUpdate
from app.api.v1.system.permission.service import PermissionService
from app.api.v1.system.user.model import User
from app.core.database import get_db
from app.web.context import admin_page_context
from app.web.deps import require_web_user
from app.web.modules.system.menu import system_path
from app.web.render import render
from app.web.utils import humanize_error

router = APIRouter(prefix="/permissions", tags=["Web System Permissions"])


async def _parent_options(db: AsyncSession):
    permissions, _ = await PermissionService(db).list_permissions(page=1, page_size=500)
    return permissions


@router.get("", response_class=HTMLResponse, name="web_system_permissions")
async def permission_list(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    permissions, total = await PermissionService(db).list_permissions(
        page=page, page_size=page_size, name=name, code=code, perm_type=type
    )
    ctx = admin_page_context(
        request,
        current_user,
        active_nav="permissions",
        title="权限管理",
        permissions=permissions,
        total=total,
        page=page,
        page_size=page_size,
        name_filter=name or "",
        code_filter=code or "",
        type_filter=type or "",
        permission_types=PERMISSION_TYPES,
        parent_options=await _parent_options(db),
        list_url=system_path("/permissions"),
    )
    return render(request, "modules/system/permissions/list.html", ctx)


@router.get("/create", response_class=HTMLResponse, name="web_system_permissions_create")
async def permission_create_form(
    request: Request,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    ctx = admin_page_context(
        request,
        current_user,
        active_nav="permissions",
        title="新建权限",
        form_action=system_path("/permissions/create"),
        perm_obj=None,
        error=None,
        parent_options=await _parent_options(db),
        permission_types=PERMISSION_TYPES,
    )
    return render(request, "modules/system/permissions/form.html", ctx)


@router.post("/create", response_class=HTMLResponse)
async def permission_create_submit(
    request: Request,
    name: str = Form(...),
    code: str = Form(...),
    type: str = Form(...),
    path: str = Form(""),
    description: str = Form(""),
    parent_id: str = Form(""),
    sort_order: int = Form(0),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    parent = int(parent_id) if parent_id.strip().isdigit() else None
    try:
        await PermissionService(db).create_permission(
            PermissionCreate(
                name=name.strip(),
                code=code.strip(),
                type=type.strip(),
                path=path.strip() or None,
                description=description.strip() or None,
                parent_id=parent,
                sort_order=sort_order,
            )
        )
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/permissions')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/permissions')}?ok=created", status_code=302)


@router.get("/{perm_id}/edit", response_class=HTMLResponse, name="web_system_permissions_edit")
async def permission_edit_form(
    request: Request,
    perm_id: int,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        perm_obj = await PermissionService(db).get_permission(perm_id)
    except ValueError:
        return RedirectResponse(f"{system_path('/permissions')}?err=权限不存在", status_code=302)
    ctx = admin_page_context(
        request,
        current_user,
        active_nav="permissions",
        title="编辑权限",
        form_action=system_path(f"/permissions/{perm_id}/edit"),
        perm_obj=perm_obj,
        error=None,
        parent_options=await _parent_options(db),
        permission_types=PERMISSION_TYPES,
    )
    return render(request, "modules/system/permissions/form.html", ctx)


@router.post("/{perm_id}/edit", response_class=HTMLResponse)
async def permission_edit_submit(
    request: Request,
    perm_id: int,
    name: str = Form(...),
    code: str = Form(...),
    type: str = Form(...),
    path: str = Form(""),
    description: str = Form(""),
    parent_id: str = Form(""),
    sort_order: int = Form(0),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    parent = int(parent_id) if parent_id.strip().isdigit() else None
    try:
        await PermissionService(db).update_permission(
            perm_id,
            PermissionUpdate(
                name=name.strip(),
                code=code.strip(),
                type=type.strip(),
                path=path.strip() or None,
                description=description.strip() or None,
                parent_id=parent,
                sort_order=sort_order,
            ),
        )
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/permissions')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/permissions')}?ok=updated", status_code=302)


@router.post("/{perm_id}/delete", name="web_system_permissions_delete")
async def permission_delete(
    perm_id: int,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await PermissionService(db).delete_permission(perm_id)
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/permissions')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/permissions')}?ok=deleted", status_code=302)
