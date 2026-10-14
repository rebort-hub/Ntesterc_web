import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALEMBIC_VERSION_DIR = os.path.join(BASE_DIR, "app", "alembic", "versions")
SEED_DATA_DIR = os.path.join(BASE_DIR, "app", "scripts", "data")
PLUGIN_DIR = os.path.join(BASE_DIR, "app", "plugin")
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
TEMPLATES_DIR = os.path.join(RESOURCES_DIR, "templates")
STATIC_DIR = os.path.join(RESOURCES_DIR, "static")
