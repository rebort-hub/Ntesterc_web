from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.settings.config import (
    ALLOWED_HOSTS,
    CORS_CREDENTIALS,
    CORS_HEADERS,
    CORS_METHODS,
    CORS_ORIGINS,
)


def path_matches_pattern(request_path: str, pattern: str) -> bool:
    if pattern.endswith("/*"):
        base_path = pattern[:-2]
        return request_path.startswith(base_path)
    return request_path == pattern


async def http_middleware(request: Request, call_next):
    excluded_patterns = [
        "/static/*",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/login",
        "/logout",
        "/admin",
        "/admin/*",
        "/login",
    ]
    if any(path_matches_pattern(request.url.path, pattern) for pattern in excluded_patterns):
        return await call_next(request)
    return await call_next(request)


def init_middleware(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
        allow_credentials=CORS_CREDENTIALS,
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=4)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=ALLOWED_HOSTS,
    )
    app.middleware("http")(http_middleware)
