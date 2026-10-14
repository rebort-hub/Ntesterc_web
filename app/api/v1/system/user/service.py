from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.system.user.model import User
from app.api.v1.system.user.repository import UserRepository
from app.api.v1.system.user.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UserRepository(db)

    async def create_user(self, user_data: UserCreate) -> User:
        if await self.repo.exists_username(user_data.username):
            raise ValueError("username exists")
        if await self.repo.exists_email(user_data.email):
            raise ValueError("email exists")
        user = User(
            username=user_data.username,
            email=user_data.email,
            is_active=user_data.is_active if user_data.is_active is not None else True,
        )
        user.set_password(user_data.password)
        return await self.repo.add(user)

    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("user not found")
        update_data = user_data.model_dump(exclude_unset=True)
        if "username" in update_data and await self.repo.exists_username(
            update_data["username"], exclude_id=user_id
        ):
            raise ValueError("username exists")
        if "email" in update_data and await self.repo.exists_email(
            update_data["email"], exclude_id=user_id
        ):
            raise ValueError("email exists")
        if "password" in update_data:
            user.set_password(update_data.pop("password"))
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete_user(self, user_id: int) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("user not found")
        await self.repo.delete(user)

    async def get_user(self, user_id: int) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise ValueError("user not found")
        return user

    async def list_users(
        self,
        page: int = 1,
        page_size: int = 10,
        username: Optional[str] = None,
        email: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[Sequence[User], int]:
        return await self.repo.list_users(page, page_size, username, email, is_active)
