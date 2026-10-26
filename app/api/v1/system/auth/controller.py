from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions.auth import MissingTokenError
from app.api.v1.system.auth.schemas import RefreshTokenResponse, TokenResponse
from app.api.v1.system.auth.service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    content_type = request.headers.get("content-type", "").lower()
    try:
        if "application/json" in content_type:
            body = await request.json()
            username, password = body.get("username"), body.get("password")
        else:
            form = await request.form()
            username, password = form.get("username"), form.get("password")
        if not username or not password:
            raise MissingTokenError()
    except Exception:
        raise MissingTokenError()
    return await AuthService(db).login(username, password)


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: Request, db: AsyncSession = Depends(get_db)
) -> RefreshTokenResponse:
    content_type = request.headers.get("content-type", "").lower()
    try:
        if "application/json" in content_type:
            token = (await request.json()).get("refresh_token")
        else:
            token = (await request.form()).get("refresh_token")
        if not token:
            raise MissingTokenError()
    except Exception:
        raise MissingTokenError()
    return await AuthService(db).refresh_token(token)


@router.post("/me")
async def read_users_me(request: Request, db: AsyncSession = Depends(get_db)):
    content_type = request.headers.get("content-type", "").lower()
    try:
        if "application/json" in content_type:
            token = (await request.json()).get("token")
        else:
            token = (await request.form()).get("token")
        if not token:
            raise MissingTokenError()
    except Exception:
        raise MissingTokenError()
    return await AuthService(db).get_user_by_token(token)
