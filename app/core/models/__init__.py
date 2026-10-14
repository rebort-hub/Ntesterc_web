import importlib
from pathlib import Path

from app.config.path_conf import PLUGIN_DIR
from app.core.models.base import Base, ModelBase, SoftDeleteMixin, TimestampMixin


def _import_plugin_models() -> None:
    plugin_root = Path(PLUGIN_DIR)
    if not plugin_root.is_dir():
        return
    for model_file in sorted(plugin_root.glob("module_*/**/model.py")):
        rel = model_file.relative_to(plugin_root)
        parts = list(rel.parts[:-1])
        module_path = "app.plugin." + ".".join(parts) + ".model"
        importlib.import_module(module_path)


def import_orm_models() -> None:
    from app.api.v1.system.permission import model as _permission  # noqa: F401
    from app.api.v1.system.role import model as _role  # noqa: F401
    from app.api.v1.system.user import model as _user  # noqa: F401
    from app.api.v1.system.user_role import model as _user_role  # noqa: F401

    _import_plugin_models()


__all__ = ["Base", "ModelBase", "TimestampMixin", "SoftDeleteMixin", "import_orm_models"]
