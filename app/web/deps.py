from typing import Optional

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.auth.service import AuthService
from app.api.v1.system.user.model import User
from app.core.database import get_db
from app.core.exceptions.auth import InvalidCredentialsError, InvalidTokenError
from app.settings.config import WEB_ACCESS_COOKIE, WEB_LOGIN_PATH


def get_access_token_from_request(request: Request) -> Optional[str]:
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return request.cookies.get(WEB_ACCESS_COOKIE)


async def get_optional_web_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    token = get_access_token_from_request(request)
    if not token:
        return None
    try:
        user, decoded = await AuthService(db).verify_token_and_get_user(token)
        if decoded.get("type") != "access":
            return None
        if not user.is_active:
            return None
        return user
    except (InvalidTokenError, InvalidCredentialsError):
        return None


async def require_web_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await get_optional_web_user(request, db)
    if user is None:
        return RedirectResponse(url=WEB_LOGIN_PATH, status_code=302)
    return user
