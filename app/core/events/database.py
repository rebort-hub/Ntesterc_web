import os

from app.config.path_conf import BASE_DIR
from app.core.database import close_db, create_tables
from app.core.migrate import upgrade_database
from app.log.config.log_config import get_logger
from app.scripts.initialize import InitializeData
from app.settings.config import (
    DATABASE_AUTO_SEED,
    DATABASE_AUTO_UPGRADE,
    DATABASE_TYPE,
    SQLITE_PATH,
)

logger = get_logger(__name__)


def _ensure_sqlite_parent_dir() -> None:
    if DATABASE_TYPE != "sqlite":
        return
    path = SQLITE_PATH if os.path.isabs(SQLITE_PATH) else os.path.join(BASE_DIR, SQLITE_PATH)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


async def init_db() -> None:
    _ensure_sqlite_parent_dir()
    try:
        if DATABASE_AUTO_UPGRADE:
            logger.info("Running Alembic upgrade...")
            upgrade_database()
        else:
            logger.info("Running create_all...")
            await create_tables()
        if DATABASE_AUTO_SEED:
            logger.info("Running seed...")
            await InitializeData().seed()
        logger.info("Database init done")
    except Exception as exc:
        logger.error("Database init failed: %s", exc)
        raise


async def shutdown_db() -> None:
    await close_db()
