"""
架构约定（对齐 backend）。

固件（稳定、与业务无关）:
  app/core/          数据库、迁移、安全、插件扫描 discover
  app/config/        路径配置
  app/settings/      config.ini
  app/log/
  app/api/v1/        API 版本入口与 system 核心骨架
  app/scripts/       应用级脚本与种子数据 app/scripts/data/*.json
  app/alembic/

核心骨架（系统能力，非插件）:
  app/api/v1/system/<feature>/   auth | user | role | permission | user_role
    controller.py | service.py | repository.py | schemas.py | model.py

业务插件（可插拔、扫描注册）:
  app/plugin/module_<name>/<feature>/controller.py
  - 顶级目录必须以 module_ 开头
  - controller 模块顶层导出 APIRouter
  - 访问路径: /api/v1/<name>/...
  - 若有表: 同目录 model.py（启动时自动 import 进 metadata）

路由:
  - 标准: /api/v1/system/...
  - 插件: /api/v1/{plugin}/...
  - 兼容: /api/...（旧前端，不在 OpenAPI 展示）

Web（前后端不分离，Jinja 页面）:
  app/web/routes/              公共页、登录、控制台
  app/web/modules/<module>/    业务大模块页面（如 system）
  resources/templates/modules/<module>/...
  resources/static/modules/<module>/...
  resources/templates/components/ui.html  公共宏: nt_table / nt_pagination / nt_modal / nt_datetime
  resources/static/css/components.css + js/components.js
  resources/static/css/theme.css + js/theme.js  主题令牌 / 暗色 / 设置抽屉
  resources/templates/errors/             403/404/405/500
  - 系统管理: /admin/system/users | roles | permissions
"""
