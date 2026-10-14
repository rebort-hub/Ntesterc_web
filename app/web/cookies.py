from fastapi import Response

from app.settings.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    WEB_ACCESS_COOKIE,
    WEB_COOKIE_SAMESITE,
    WEB_COOKIE_SECURE,
    WEB_REFRESH_COOKIE,
)


def _cookie_kwargs(max_age: int) -> dict:
    return {
        "httponly": True,
        "secure": WEB_COOKIE_SECURE,
        "samesite": WEB_COOKIE_SAMESITE,
        "max_age": max_age,
        "path": "/",
    }


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        WEB_ACCESS_COOKIE,
        access_token,
        **_cookie_kwargs(JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60),
    )
    response.set_cookie(
        WEB_REFRESH_COOKIE,
        refresh_token,
        **_cookie_kwargs(JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600),
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(WEB_ACCESS_COOKIE, path="/")
    response.delete_cookie(WEB_REFRESH_COOKIE, path="/")
