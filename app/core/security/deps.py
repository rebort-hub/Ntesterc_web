from typing import Callable, List, Set, Union

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.user.model import User
from app.api.v1.system.user.repository import UserRepository
from app.api.v1.system.user_role.repository import UserRoleRepository
from app.core.database import get_db
from app.settings import config as settings
from app.settings.config import WEB_ACCESS_COOKIE

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/system/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/api/v1/system/auth/login",
    auto_error=False,
)


def _resolve_access_token(request: Request, bearer: str | None) -> str | None:
    if bearer:
        return bearer
    return request.cookies.get(WEB_ACCESS_COOKIE)


async def get_current_user(
    request: Request,
    bearer: str | None = Depends(oauth2_scheme_optional),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = _resolve_access_token(request, bearer)
    if not token:
        raise credentials_exception
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("uid")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await UserRepository(db).get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
    return user


async def get_current_active_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser required",
        )
    return current_user


async def get_current_user_permissions(current_user: User, db: AsyncSession) -> Set[str]:
    if current_user.is_superadmin:
        return {"*"}
    return await UserRoleRepository(db).get_permission_codes_for_user(current_user.id)


async def get_current_user_roles(current_user: User, db: AsyncSession) -> Set[str]:
    return await UserRoleRepository(db).get_role_codes_for_user(current_user.id)


def require_permissions(permissions: Union[str, List[str]], require_all: bool = True):
    if isinstance(permissions, str):
        permissions = [permissions]

    async def check_permissions(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_superadmin:
            return
        user_permissions = await get_current_user_permissions(current_user, db)
        if require_all:
            if not all(perm in user_permissions for perm in permissions):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        elif not any(perm in user_permissions for perm in permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return check_permissions


def require_roles(roles: Union[str, List[str]], require_all: bool = True):
    if isinstance(roles, str):
        roles = [roles]

    async def check_roles(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_superadmin:
            return
        user_roles = await get_current_user_roles(current_user, db)
        if require_all:
            if not all(role in user_roles for role in roles):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        elif not any(role in user_roles for role in roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return check_roles


def require_active_user():
    async def check_active(current_user: User = Depends(get_current_user)):
        if not current_user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User disabled")
        return current_user

    return check_active


def require_superuser():
    async def check_superuser(current_user: User = Depends(get_current_user)):
        if not current_user.is_superadmin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser required")
        return current_user

    return check_superuser


def require_any(*requirements: Callable) -> Callable:
    async def check_any(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_superadmin:
            return
        errors = []
        for requirement in requirements:
            try:
                await requirement()(current_user, db)
                return
            except HTTPException as e:
                errors.append(str(e.detail))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=" OR ".join(errors),
        )

    return check_any


def require_all(*requirements: Callable) -> Callable:
    async def check_all(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db),
    ):
        if current_user.is_superadmin:
            return
        for requirement in requirements:
            await requirement()(current_user, db)

    return check_all
