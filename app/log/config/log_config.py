import logging
import sys

from app.settings.config import (
    LOG_BACKUP_COUNT,
    LOG_CONSOLE_OUTPUT,
    LOG_FILE_ENABLED,
    LOG_FILE_PATH,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_MAX_SIZE,
)


def setup_logging() -> None:
    root = logging.getLogger()
    root.setLevel(LOG_LEVEL)
    root.handlers.clear()
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    if LOG_FILE_ENABLED:
        from logging.handlers import RotatingFileHandler

        fh = RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=LOG_MAX_SIZE,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        fh.setFormatter(formatter)
        root.addHandler(fh)
    if LOG_CONSOLE_OUTPUT:
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        root.addHandler(ch)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
