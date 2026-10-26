"""Web HTML 错误页渲染。"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse, Response

from app.log.config.log_config import get_logger
from app.web.render import render

logger = get_logger(__name__)

_STATUS_TEMPLATES = {
    403: "errors/403.html",
    404: "errors/404.html",
    405: "errors/405.html",
    500: "errors/500.html",
}


def _wants_html(request: Request) -> bool:
    path = request.url.path or ""
    if path.startswith("/api/"):
        return False
    accept = (request.headers.get("accept") or "").lower()
    if "application/json" in accept and "text/html" not in accept:
        return False
    return True


def _error_page(request: Request, status_code: int) -> Response:
    template = _STATUS_TEMPLATES.get(status_code, "errors/500.html")
    return render(
        request,
        template,
        {"title": str(status_code)},
        status_code=status_code,
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if _wants_html(request) and exc.status_code in _STATUS_TEMPLATES:
            return _error_page(request, exc.status_code)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(status_code=422, content={"detail": exc.errors()})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("未处理异常: %s", exc)
        if _wants_html(request):
            return _error_page(request, 500)
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})
