"""权限/菜单图标"""

from __future__ import annotations

# 旧短名 → layui 字形（兼容已入库数据）
ICON_ALIASES: dict[str, str] = {
    "dashboard": "layui-icon-console",
    "setting": "layui-icon-set",
    "user": "layui-icon-user",
    "team": "layui-icon-group",
    "safety": "layui-icon-vercode",
    "folder": "layui-icon-file",
    "dot": "layui-icon-circle-dot",
    "app": "layui-icon-app",
    "file": "layui-icon-file",
    "edit": "layui-icon-edit",
    "delete": "layui-icon-delete",
    "search": "layui-icon-search",
    "lock": "layui-icon-password",
    "key": "layui-icon-password",
    "unlock": "layui-icon-password",
    "notice": "layui-icon-notice",
    "theme": "layui-icon-theme",
    "chart": "layui-icon-chart",
    "cloud": "layui-icon-website",
    "link": "layui-icon-link",
    "star": "layui-icon-star",
    "heart": "layui-icon-rate",
    "camera": "layui-icon-camera",
    "cart": "layui-icon-cart",
    "video": "layui-icon-video",
    "voice": "layui-icon-voice",
    "upload": "layui-icon-upload",
    "download": "layui-icon-download-circle",
    "play": "layui-icon-play",
    "pause": "layui-icon-pause",
    "more": "layui-icon-more",
    "location": "layui-icon-location",
    "flag": "layui-icon-flag",
    "fire": "layui-icon-fire",
    "diamond": "layui-icon-diamond",
    "console": "layui-icon-console",
    "template": "layui-icon-template",
    "male": "layui-icon-male",
    "female": "layui-icon-female",
    "smile": "layui-icon-face-smile",
    "cry": "layui-icon-face-cry",
    "refresh": "layui-icon-refresh",
    "tip": "layui-icon-tips",
    "note": "layui-icon-note",
    "website": "layui-icon-website",
    "component": "layui-icon-component",
    "add": "layui-icon-add-1",
    "check": "layui-icon-ok",
    "close": "layui-icon-close",
    "menu": "layui-icon-menu-fill",
    "grid": "layui-icon-app",
    "list": "layui-icon-list",
    "print": "layui-icon-file",
    "export": "layui-icon-release",
    "shield": "layui-icon-auz",
    "database": "layui-icon-templeate-1",
    "server": "layui-icon-engine",
    "code": "layui-icon-fonts-code",
    "api": "layui-icon-util",
    "power": "layui-icon-set-fill",
    "folder-open": "layui-icon-file-b",
    "mail": "layui-icon-dialogue",
    "phone": "layui-icon-cellphone",
    "calendar": "layui-icon-date",
    "clock": "layui-icon-log",
    "tag": "layui-icon-tabs",
    "home": "layui-icon-home",
}


def normalize_icon(icon: str | None, *, default: str = "layui-icon-circle-dot") -> str:
    """返回可直接放在 class 上的字形类，如 layui-icon-set。"""
    raw = (icon or "").strip()
    if not raw:
        return default
    # rebort 入库格式：layui-icon layui-icon-home
    if " " in raw:
        for part in raw.split():
            if part.startswith("layui-icon-"):
                return part
        return default
    if raw.startswith("layui-icon-"):
        return raw
    if raw.startswith("layui-icon"):
        return default
    return ICON_ALIASES.get(raw, default)


def icon_classes(icon: str | None, *, default: str = "layui-icon-circle-dot") -> str:
    """完整 class：layui-icon layui-icon-xxx"""
    glyph = normalize_icon(icon, default=default)
    return f"layui-icon {glyph}"
