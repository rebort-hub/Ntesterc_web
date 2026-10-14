import os

from fastapi.templating import Jinja2Templates

from app.config.path_conf import TEMPLATES_DIR

os.makedirs(TEMPLATES_DIR, exist_ok=True)

templates = Jinja2Templates(directory=TEMPLATES_DIR)
