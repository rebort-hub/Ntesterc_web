from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.models import import_orm_models
from app.core.models.base import Base
from app.log.config.log_config import get_logger
from app.settings.config import ASYNC_DATABASE_URL, DATABASE_ECHO

import_orm_models()

logger = get_logger(__name__)

async_engine: AsyncEngine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=DATABASE_ECHO,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("create_all finished")


async def close_db() -> None:
    await async_engine.dispose()
    logger.info("database connections closed")
