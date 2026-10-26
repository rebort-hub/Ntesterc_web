import os
from alembic import command
from alembic.config import Config
from app.config.path_conf import BASE_DIR, ALEMBIC_VERSION_DIR
from app.settings.config import SYNC_DATABASE_URL


def get_alembic_config() -> Config:
    cfg = Config(os.path.join(BASE_DIR, "alembic.ini"))
    cfg.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)
    return cfg


def upgrade_database(revision: str = "head") -> None:
    os.makedirs(ALEMBIC_VERSION_DIR, exist_ok=True)
    command.upgrade(get_alembic_config(), revision)


def revision_database(message: str = "迁移脚本", autogenerate: bool = True) -> None:
    os.makedirs(ALEMBIC_VERSION_DIR, exist_ok=True)
    command.revision(
        get_alembic_config(),
        message=message,
        autogenerate=autogenerate,
    )
