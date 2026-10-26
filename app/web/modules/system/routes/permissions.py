from typing import Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.permission.model import PERMISSION_OPEN_TYPES, PERMISSION_TYPES
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

TYPE_LABELS = {
    "directory": "目录",
    "menu": "菜单",
    "button": "按钮",
    "api": "接口",
}
OPEN_TYPE_LABELS = {
    "_self": "当前页",
    "_blank": "新窗口",
    "_iframe": "框架页签",
}


async def _parent_options(db: AsyncSession):
    permissions, _ = await PermissionService(db).list_permissions(page=1, page_size=500)
    return permissions


def _form_payload(
    name: str,
    code: str,
    type: str,
    path: str,
    description: str,
    parent_id: str,
    sort_order: int,
    icon: str,
    open_type: str,
    is_enabled: bool = True,
) -> PermissionCreate:
    parent = int(parent_id) if parent_id.strip().isdigit() else None
    return PermissionCreate(
        name=name.strip(),
        code=code.strip(),
        type=type.strip(),
        path=path.strip() or None,
        description=description.strip() or None,
        parent_id=parent,
        sort_order=sort_order,
        icon=icon.strip() or None,
        open_type=open_type.strip() or None,
        is_enabled=is_enabled,
    )


def _parse_enabled(raw: Optional[str]) -> bool:
    return raw in ("on", "true", "1", "yes")


@router.get("", response_class=HTMLResponse, name="web_system_permissions")
async def permission_list(
    request: Request,
    name: Optional[str] = Query(None),
    code: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    tree = await PermissionService(db).get_permission_tree()
    # 简单过滤：按名称/编码/类型裁剪树（保留匹配节点及其祖先）
    if name or code or type:
        tree = _filter_tree(tree, name=name, code=code, perm_type=type)

    ctx = await admin_page_context(
        request,
        current_user,
        active_nav="permissions",
        title="权限管理",
        db=db,
        permission_tree=tree,
        name_filter=name or "",
        code_filter=code or "",
        type_filter=type or "",
        permission_types=PERMISSION_TYPES,
        type_labels=TYPE_LABELS,
        open_types=PERMISSION_OPEN_TYPES,
        open_type_labels=OPEN_TYPE_LABELS,
        parent_options=await _parent_options(db),
        list_url=system_path("/permissions"),
    )
    return render(request, "modules/system/permissions/list.html", ctx)


def _filter_tree(nodes, name=None, code=None, perm_type=None):
    from app.api.v1.system.permission.schemas import PermissionTreeNode

    result = []
    for n in nodes:
        kids = _filter_tree(n.children, name, code, perm_type)
        self_ok = True
        if name and name.lower() not in (n.name or "").lower():
            self_ok = False
        if code and code.lower() not in (n.code or "").lower():
            self_ok = False
        if perm_type and n.type != perm_type:
            self_ok = False
        if self_ok or kids:
            data = n.model_dump()
            data["children"] = kids
            result.append(PermissionTreeNode(**data))
    return result


@router.get("/create", response_class=HTMLResponse, name="web_system_permissions_create")
async def permission_create_form(
    request: Request,
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    ctx = await admin_page_context(
        request,
        current_user,
        active_nav="permissions",
        title="新建权限",
        db=db,
        form_action=system_path("/permissions/create"),
        perm_obj=None,
        error=None,
        parent_options=await _parent_options(db),
        permission_types=PERMISSION_TYPES,
        type_labels=TYPE_LABELS,
        open_types=PERMISSION_OPEN_TYPES,
        open_type_labels=OPEN_TYPE_LABELS,
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
    icon: str = Form(""),
    open_type: str = Form(""),
    is_enabled: Optional[str] = Form(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await PermissionService(db).create_permission(
            _form_payload(
                name,
                code,
                type,
                path,
                description,
                parent_id,
                sort_order,
                icon,
                open_type,
                _parse_enabled(is_enabled),
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
    ctx = await admin_page_context(
        request,
        current_user,
        active_nav="permissions",
        title="编辑权限",
        db=db,
        form_action=system_path(f"/permissions/{perm_id}/edit"),
        perm_obj=perm_obj,
        error=None,
        parent_options=await _parent_options(db),
        permission_types=PERMISSION_TYPES,
        type_labels=TYPE_LABELS,
        open_types=PERMISSION_OPEN_TYPES,
        open_type_labels=OPEN_TYPE_LABELS,
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
    icon: str = Form(""),
    open_type: str = Form(""),
    is_enabled: Optional[str] = Form(None),
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
                icon=icon.strip() or None,
                open_type=open_type.strip() or None,
                is_enabled=_parse_enabled(is_enabled),
            ),
        )
    except ValueError as e:
        await db.rollback()
        return RedirectResponse(
            f"{system_path('/permissions')}?err={humanize_error(e)}",
            status_code=302,
        )
    return RedirectResponse(f"{system_path('/permissions')}?ok=updated", status_code=302)


@router.post("/{perm_id}/enable", name="web_system_permissions_enable")
async def permission_set_enable(
    perm_id: int,
    is_enabled: Optional[str] = Form(None),
    current_user: User = Depends(require_web_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        await PermissionService(db).set_enabled(perm_id, _parse_enabled(is_enabled))
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
