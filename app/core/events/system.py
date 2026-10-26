import os
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import router as main_router
from app.config.path_conf import STATIC_DIR
from app.core.events.database import init_db, shutdown_db
from app.core.events.middleware import init_middleware
from app.log.config.log_config import get_logger, setup_logging
from app.settings.config import (
    APP_DESCRIPTION,
    APP_NAME,
    APP_VERSION,
    SERVER_HOST,
    SERVER_PORT,
    WEB_ENABLED,
)

logger = get_logger(__name__)


class SystemInit:
    """应用生命周期与 FastAPI 初始化。"""

    def __init__(self):
        self.app: Optional[FastAPI] = None
        self.static_path = STATIC_DIR

    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        logger.info("应用程序启动")
        await init_db()
        logger.info("服务地址: http://%s:%s", SERVER_HOST, SERVER_PORT)
        yield
        await shutdown_db()
        logger.info("应用程序关闭")

    def init_app(self) -> FastAPI:
        setup_logging()
        self.app = FastAPI(
            title=APP_NAME,
            version=APP_VERSION,
            description=APP_DESCRIPTION,
            lifespan=self.lifespan,
        )
        init_middleware(self.app)
        if WEB_ENABLED:
            self._init_static()
            from app.web.errors import register_error_handlers

            register_error_handlers(self.app)
        self.app.include_router(main_router)
        return self.app

    def _init_static(self):
        os.makedirs(self.static_path, exist_ok=True)
        self.app.mount("/static", StaticFiles(directory=self.static_path), name="static")


system = SystemInit()
