from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security.deps import (
    get_current_active_superuser,
    get_current_user,
    get_current_user_permissions,
    get_current_user_roles,
    require_active_user,
    require_all,
    require_any,
    require_permissions,
    require_roles,
    require_superuser,
)
from app.api.v1.system.user.model import User
from app.api.v1.system.user.schemas import UserCreate, UserList, UserResponse, UserUpdate
from app.api.v1.system.user.service import UserService

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await UserService(db).create_user(user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await UserService(db).update_user(user_id, user_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_current_active_superuser)],
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        await UserService(db).delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return await UserService(db).get_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("", response_model=UserList)
async def list_users(
    page: int = 1,
    page_size: int = 10,
    username: Optional[str] = None,
    email: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users, total = await UserService(db).list_users(
        page=page,
        page_size=page_size,
        username=username,
        email=email,
        is_active=is_active,
    )
    return {"total": total, "items": users}


@router.get(
    "/me/me",
    response_model=UserResponse,
    dependencies=[Depends(require_active_user())],
)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/{user_id}/activate",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_any(
                lambda: require_roles("admin"),
                lambda: require_permissions(["user.manage", "user.reset-password"]),
            )
        )
    ],
)
async def activate_user(user_id: int, current_user: User = Depends(get_current_user)):
    return {"message": "访问成功", "user_id": user_id}


@router.post(
    "/{user_id}/deactivate",
    status_code=status.HTTP_200_OK,
    dependencies=[
        Depends(
            require_all(
                lambda: require_permissions("user.manage"),
                lambda: require_roles(["admin", "supervisor"], require_all=False),
            )
        )
    ],
)
async def deactivate_user(user_id: int, current_user: User = Depends(get_current_user)):
    return {"message": "访问成功", "user_id": user_id}


@router.post(
    "/{user_id}/reset-password",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_superuser())],
)
async def reset_user_password(user_id: int):
    return {"message": "访问成功", "user_id": user_id}


@router.get("/admin/dashboard", dependencies=[Depends(require_roles("admin"))])
async def admin_dashboard():
    return {"message": "访问成功"}


@router.get("/me/permissions", response_model=List[str])
async def get_my_permissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return list(await get_current_user_permissions(current_user, db))


@router.get("/me/roles", response_model=List[str])
async def get_my_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return list(await get_current_user_roles(current_user, db))
