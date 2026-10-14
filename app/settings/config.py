import os
from configparser import ConfigParser
from datetime import timedelta
from typing import List, Tuple
from urllib.parse import quote_plus

from app.config.path_conf import BASE_DIR

config = ConfigParser()
config_file = os.path.join(BASE_DIR, "config.ini")
config.read(config_file, encoding="utf-8")

APP_NAME = config.get("APP", "APP_NAME")
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "NtestercWeb API"
DEBUG = config.getboolean("APP", "DEBUG")
SECRET_KEY = config.get("APP", "SECRET_KEY")
ALLOWED_HOSTS: List[str] = [
    host.strip() for host in config.get("APP", "ALLOWED_HOSTS").split(",") if host.strip()
]

SERVER_HOST = config.get("SERVER", "HOST")
SERVER_PORT = config.getint("SERVER", "PORT")
SERVER_RELOAD = config.getboolean("SERVER", "RELOAD")
SERVER_WORKERS = config.getint("SERVER", "WORKERS")
SERVER_LOG_LEVEL = config.get("SERVER", "LOG_LEVEL").lower()

DATABASE_TYPE = config.get("DATABASE", "TYPE", fallback="sqlite").strip().lower()
DATABASE_HOST = config.get("DATABASE", "HOST", fallback="127.0.0.1")
DATABASE_PORT = config.getint("DATABASE", "PORT", fallback=3306)
DATABASE_USER = config.get("DATABASE", "USER", fallback="root")
DATABASE_PASSWORD = config.get("DATABASE", "PASSWORD", fallback="")
DATABASE_NAME = config.get("DATABASE", "NAME", fallback="ntesterc")
SQLITE_PATH = config.get("DATABASE", "SQLITE_PATH", fallback="resources/db.sqlite3")
DATABASE_URL_OVERRIDE = config.get("DATABASE", "DATABASE_URL", fallback="").strip()
DATABASE_ECHO = config.getboolean("DATABASE", "ECHO", fallback=False)
DATABASE_AUTO_UPGRADE = config.getboolean("DATABASE", "AUTO_UPGRADE", fallback=True)
DATABASE_AUTO_SEED = config.getboolean("DATABASE", "AUTO_SEED", fallback=True)


def _sqlite_file_path() -> str:
    if os.path.isabs(SQLITE_PATH):
        return SQLITE_PATH.replace("\\", "/")
    return os.path.join(BASE_DIR, SQLITE_PATH).replace("\\", "/")


def _build_sync_database_url() -> str:
    if DATABASE_URL_OVERRIDE:
        return DATABASE_URL_OVERRIDE
    if DATABASE_TYPE == "sqlite":
        return f"sqlite:///{_sqlite_file_path()}"
    if DATABASE_TYPE == "mysql":
        password = quote_plus(DATABASE_PASSWORD)
        return (
            f"mysql+pymysql://{DATABASE_USER}:{password}"
            f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}?charset=utf8mb4"
        )
    if DATABASE_TYPE in ("postgres", "postgresql"):
        password = quote_plus(DATABASE_PASSWORD)
        return (
            f"postgresql+psycopg://{DATABASE_USER}:{password}"
            f"@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
        )
    raise ValueError(f"Unsupported DATABASE_TYPE: {DATABASE_TYPE}")


def _to_async_url(sync_url: str) -> str:
    if sync_url.startswith("sqlite:///"):
        return sync_url.replace("sqlite:///", "sqlite+aiosqlite:///", 1)
    if sync_url.startswith("mysql+pymysql://"):
        return sync_url.replace("mysql+pymysql://", "mysql+asyncmy://", 1)
    if sync_url.startswith("postgresql+psycopg://"):
        return sync_url.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
    if "+async" in sync_url:
        return sync_url
    raise ValueError(f"Cannot convert to async URL: {sync_url}")


def get_database_urls() -> Tuple[str, str]:
    sync_url = _build_sync_database_url()
    return sync_url, _to_async_url(sync_url)


SYNC_DATABASE_URL, ASYNC_DATABASE_URL = get_database_urls()

JWT_SECRET_KEY = config.get("JWT", "SECRET_KEY")
JWT_ALGORITHM = config.get("JWT", "ALGORITHM")
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = config.getint("JWT", "ACCESS_TOKEN_EXPIRE_MINUTES")
JWT_REFRESH_TOKEN_EXPIRE_DAYS = config.getint("JWT", "REFRESH_TOKEN_EXPIRE_DAYS")

ACCESS_TOKEN_EXPIRE_DELTA = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
REFRESH_TOKEN_EXPIRE_DELTA = timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)

LOG_LEVEL = config.get("LOG", "LEVEL")
LOG_FORMAT = config.get("LOG", "FORMAT")
LOG_FILE_ENABLED = config.getboolean("LOG", "FILE_ENABLED")
LOG_FILE_PATH = os.path.join(BASE_DIR, config.get("LOG", "FILE_PATH"))
LOG_MAX_SIZE = config.getint("LOG", "MAX_SIZE") * 1024 * 1024
LOG_BACKUP_COUNT = config.getint("LOG", "BACKUP_COUNT")
LOG_CONSOLE_OUTPUT = config.getboolean("LOG", "CONSOLE_OUTPUT")

CORS_ORIGINS = eval(config.get("CORS", "ORIGINS"))
CORS_METHODS = eval(config.get("CORS", "METHODS"))
CORS_HEADERS = eval(config.get("CORS", "HEADERS"))
CORS_CREDENTIALS = config.getboolean("CORS", "ALLOW_CREDENTIALS")

WEB_ENABLED = config.getboolean("WEB", "ENABLED", fallback=True)
WEB_ADMIN_PREFIX = config.get("WEB", "ADMIN_PREFIX", fallback="/admin").rstrip("/") or "/admin"
WEB_LOGIN_PATH = config.get("WEB", "LOGIN_PATH", fallback="/login")
WEB_LOGIN_REDIRECT = config.get("WEB", "LOGIN_REDIRECT", fallback="/admin")
WEB_ACCESS_COOKIE = config.get("WEB", "ACCESS_COOKIE", fallback="ntesterc_access_token")
WEB_REFRESH_COOKIE = config.get("WEB", "REFRESH_COOKIE", fallback="ntesterc_refresh_token")
WEB_COOKIE_SECURE = config.getboolean("WEB", "COOKIE_SECURE", fallback=False)
WEB_COOKIE_SAMESITE = config.get("WEB", "COOKIE_SAMESITE", fallback="lax").lower()
