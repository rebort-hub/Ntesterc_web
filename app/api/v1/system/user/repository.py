from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.system.user.model import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(
            select(User).where(User.username == username, User.is_deleted.is_(False))
        )
        return result.scalar_one_or_none()

    async def exists_username(self, username: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(User.id).where(User.username == username, User.is_deleted.is_(False))
        if exclude_id is not None:
            stmt = stmt.where(User.id != exclude_id)
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none() is not None

    async def exists_email(self, email: str, exclude_id: Optional[int] = None) -> bool:
        stmt = select(User.id).where(User.email == email, User.is_deleted.is_(False))
        if exclude_id is not None:
            stmt = stmt.where(User.id != exclude_id)
        result = await self.db.execute(stmt.limit(1))
        return result.scalar_one_or_none() is not None

    async def add(self, user: User) -> User:
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)

    async def list_users(
        self,
        page: int,
        page_size: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[Sequence[User], int]:
        filters = [User.is_deleted.is_(False)]
        if username:
            filters.append(User.username.ilike(f"%{username}%"))
        if email:
            filters.append(User.email.ilike(f"%{email}%"))
        if is_active is not None:
            filters.append(User.is_active.is_(is_active))

        total = (
            await self.db.execute(select(func.count()).select_from(User).where(*filters))
        ).scalar_one()

        stmt = (
            select(User)
            .where(*filters)
            .order_by(User.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        users = (await self.db.execute(stmt)).scalars().all()
        return users, total
