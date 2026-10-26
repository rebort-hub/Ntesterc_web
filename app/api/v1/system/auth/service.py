from datetime import datetime
from typing import Annotated, Any, Dict, Optional, Tuple
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions.auth import (
    InvalidCredentialsError,
    InvalidTokenError,
    InvalidTokenTypeError,
    UserNotFoundError,
)
from app.core.security.token import (
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    verify_token,
)
from app.api.v1.system.auth.schemas import RefreshTokenResponse, TokenResponse
from app.api.v1.system.user.model import User
from app.api.v1.system.user.repository import UserRepository
from app.settings.config import (
    ACCESS_TOKEN_EXPIRE_DELTA,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DELTA,
)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.users = UserRepository(db)

    async def authenticate_user(self, username: str, password: str) -> User:
        user = await self.users.get_by_username(username)
        if not user or not user.verify_password(password):
            raise InvalidCredentialsError()
        return user

    async def verify_token_and_get_user(self, token: str) -> Tuple[User, Dict[str, Any]]:
        try:
            decoded_token = verify_token(token)
            user = await self.users.get_by_id(int(decoded_token["uid"]))
            if not user:
                raise UserNotFoundError()
            return user, decoded_token
        except Exception:
            raise InvalidTokenError()

    def create_tokens(self, user: User) -> TokenResponse:
        token_data = {"uid": user.id, "sub": user.username, "scopes": []}
        access_token = create_access_token({**token_data, "type": "access"})
        refresh_token = create_refresh_token({**token_data, "type": "refresh"})
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=int(ACCESS_TOKEN_EXPIRE_DELTA.total_seconds()),
            refresh_expires_in=int(REFRESH_TOKEN_EXPIRE_DELTA.total_seconds()),
        )

    @classmethod
    async def get_current_user(
        cls,
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> User:
        try:
            payload = verify_token(token)
            uid = payload.get("uid")
            username = payload.get("sub")
            token_type = payload.get("type")
            if not uid or not username or not token_type:
                raise InvalidTokenError()
            if token_type != "access":
                raise InvalidTokenTypeError()
            user = await UserRepository(db).get_by_id(int(uid))
            if user is None:
                raise UserNotFoundError()
            return user
        except (InvalidTokenTypeError, UserNotFoundError):
            raise
        except Exception:
            raise InvalidTokenError()

    async def update_last_login(self, user: User) -> None:
        user.last_login = datetime.now()
        await self.db.flush()

    def get_user_response(self, user: User) -> Dict[str, Any]:
        return {
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_superadmin": user.is_superadmin,
            "last_login": user.last_login,
        }

    async def login(self, username: str, password: str) -> TokenResponse:
        user = await self.authenticate_user(username, password)
        await self.update_last_login(user)
        return self.create_tokens(user)

    async def refresh_token(self, token: str) -> RefreshTokenResponse:
        user, decoded = await self.verify_token_and_get_user(token)
        if decoded.get("type") != "refresh":
            raise InvalidTokenTypeError()
        token_data = {"uid": user.id, "sub": user.username, "scopes": []}
        access_token = create_access_token({**token_data, "type": "access"})
        return RefreshTokenResponse(
            access_token=access_token,
            expires_in=JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def get_user_by_token(self, token: str) -> Dict[str, Any]:
        user, decoded = await self.verify_token_and_get_user(token)
        return {
            "token_type": decoded.get("type"),
            "user": self.get_user_response(user),
        }
