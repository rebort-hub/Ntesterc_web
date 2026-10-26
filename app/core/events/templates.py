import os

from fastapi.templating import Jinja2Templates

from app.config.path_conf import TEMPLATES_DIR
from app.core.icons import icon_classes, normalize_icon

os.makedirs(TEMPLATES_DIR, exist_ok=True)

templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.filters["nt_icon"] = normalize_icon
templates.env.filters["nt_icon_class"] = icon_classes
