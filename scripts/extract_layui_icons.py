"""Extract layui-icon CSS (+ copy fonts) for Ntesterc static assets."""
from __future__ import annotations

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_CSS = ROOT / "rebort/static/system/component/layui/css/layui.css"
SRC_FONT = ROOT / "rebort/static/system/component/layui/font"
DST_FONT = ROOT / "resources/static/fonts/layui"
DST_CSS = ROOT / "resources/static/css/layui-icons.css"


def main() -> None:
    DST_FONT.mkdir(parents=True, exist_ok=True)
    for f in SRC_FONT.iterdir():
        if f.is_file():
            shutil.copy2(f, DST_FONT / f.name)

    css = SRC_CSS.read_text(encoding="utf-8", errors="ignore")
    out: list[str] = [
        "/* Layui iconfont extracted for Ntesterc (font only, no Layui JS) */",
        "@font-face{",
        "font-family:layui-icon;",
        "src:url(../fonts/layui/iconfont.eot?v=256);",
        "src:url(../fonts/layui/iconfont.eot?v=256#iefix) format('embedded-opentype'),",
        "url(../fonts/layui/iconfont.woff2?v=256) format('woff2'),",
        "url(../fonts/layui/iconfont.woff?v=256) format('woff'),",
        "url(../fonts/layui/iconfont.ttf?v=256) format('truetype'),",
        "url(../fonts/layui/iconfont.svg?v=256#layui-icon) format('svg')",
        "}",
        ".layui-icon{",
        "font-family:layui-icon!important;",
        "font-size:16px;",
        "font-style:normal;",
        "-webkit-font-smoothing:antialiased;",
        "-moz-osx-font-smoothing:grayscale",
        "}",
    ]
    seen: set[str] = set()
    for m in re.finditer(r"(\.layui-icon-[a-z0-9-]+):before\{content:(\"[^\"]+\")\}", css):
        cls, content = m.group(1), m.group(2)
        if cls in seen:
            continue
        seen.add(cls)
        out.append(f"{cls}:before{{content:{content}}}")

    DST_CSS.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"copied fonts -> {DST_FONT}")
    print(f"wrote {DST_CSS} ({len(seen)} icons)")


if __name__ == "__main__":
    main()
