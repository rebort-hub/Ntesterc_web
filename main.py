import sys
from app.core.events.system import system
from app.core.migrate import revision_database, upgrade_database
from app.log.config.log_config import get_logger
from app.settings.config import (
    SERVER_HOST,
    SERVER_LOG_LEVEL,
    SERVER_PORT,
    SERVER_RELOAD,
    SERVER_WORKERS,
)

app = system.init_app()
logger = get_logger(__name__)


def _print_usage() -> None:
    print(
        "用法:\n"
        "  python main.py              启动开发服务器\n"
        "  python main.py upgrade      应用 Alembic 迁移到 head\n"
        "  python main.py revision     自动生成迁移脚本\n"
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "upgrade":
            upgrade_database()
            logger.info("数据库迁移已完成")
            sys.exit(0)
        if command == "revision":
            revision_database()
            logger.info("迁移脚本已生成")
            sys.exit(0)
        if command in ("-h", "--help", "help"):
            _print_usage()
            sys.exit(0)
        print(f"未知命令: {command}")
        _print_usage()
        sys.exit(1)

    import uvicorn

    logger.info("正在启动开发服务器")
    uvicorn.run(
        "main:app",host=SERVER_HOST,port=SERVER_PORT,reload=SERVER_RELOAD,workers=SERVER_WORKERS or None,log_level=SERVER_LOG_LEVEL,
    )
