import importlib
from pathlib import Path
from fastapi import APIRouter
from app.log.config.log_config import get_logger

logger = get_logger(__name__)


def get_plugin_router() -> APIRouter:
    """扫描 ``app/plugin`` 并注册所有插件路由。"""
    root_router = APIRouter()
    seen_router_ids: set[int] = set()

    try:
        base_package = importlib.import_module("app.plugin")
        base_dir = Path(next(iter(base_package.__path__)))
        controller_files = sorted(base_dir.glob("module_*/**/controller.py"))
        container_routers: dict[str, APIRouter] = {}

        for file in controller_files:
            rel_path = file.relative_to(base_dir)
            path_parts = rel_path.parts
            top_module = path_parts[0]
            suffix = top_module[7:] if top_module.startswith("module_") else ""
            if not suffix:
                logger.warning("跳过非法插件目录: %s", top_module)
                continue
            prefix = f"/{suffix}"
            if prefix not in container_routers:
                container_routers[prefix] = APIRouter(prefix=prefix)
            container_router = container_routers[prefix]
            module_path = f"app.plugin.{'.'.join(path_parts[:-1])}.controller"

            try:
                module = importlib.import_module(module_path)
                registered = 0
                for attr_name in dir(module):
                    attr_value = getattr(module, attr_name, None)
                    if isinstance(attr_value, APIRouter):
                        router_id = id(attr_value)
                        if router_id not in seen_router_ids:
                            seen_router_ids.add(router_id)
                            container_router.include_router(attr_value)
                            registered += 1
                if registered == 0:
                    logger.warning("插件 controller 未导出 APIRouter: %s", module_path)
            except Exception as exc:
                logger.exception("加载插件 controller 失败 %s: %s", module_path, exc)

        for prefix, container_router in sorted(container_routers.items()):
            root_router.include_router(container_router)
            logger.info("已注册插件路由容器 %s（%s 条）", prefix, len(container_router.routes))

    except Exception as exc:
        logger.exception("插件路由扫描失败: %s", exc)

    return root_router
