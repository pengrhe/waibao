"""
Generate 8 tabbar icons (4 tabs × normal/selected) as 60x60 PNGs.

Approach: hand-write Material-Symbols-inspired SVG paths, then rasterize with
svglib + reportlab (pure Python, no native deps required on Windows).

Tabs: home / gallery / cart / mine

Output: aitee/miniapp/src/static/img/tabbar/{home,gallery,cart,mine}{,-active}.png
Run from anywhere:
    python aitee/miniapp/scripts/gen_tabbar_icons.py
"""
from __future__ import annotations

import io
import os
import sys

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "src", "static", "img", "tabbar")
)
os.makedirs(ROOT, exist_ok=True)

NORMAL = "#94a3b8"   # slate-400
SELECTED = "#ff4d6e" # brand red

# All paths designed for a 24×24 viewport, Material-Symbols-Rounded inspired.
# Filled silhouettes with rounded corners, modern e-commerce aesthetic.

ICON_PATHS = {
    # 房子：圆角五边形屋顶 + 屋身 + 镂空门
    "home": (
        "M11.29 3.4 4.46 8.62a2 2 0 0 0-.79 1.59V19a2 2 0 0 0 2 2h3.5a1 1 0 0 0 1-1v-4.5"
        "a1.5 1.5 0 1 1 3 0V20a1 1 0 0 0 1 1h3.5a2 2 0 0 0 2-2v-8.79a2 2 0 0 0-.79-1.59"
        "L13.04 3.4a1.5 1.5 0 0 0-1.75 0Z"
    ),
    # 印花库：两张错位卡片 + 右上角 sparkle，明确"图案库"含义
    "gallery_card_back": (
        "M7 6h10a3 3 0 0 1 3 3v9a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V9a3 3 0 0 1 3-3Z"
    ),
    # 印花库前景卡片（叠加）+ sparkle 4 角星
    "gallery_card_front": (
        "M5 4h8a3 3 0 0 1 3 3v8a3 3 0 0 1-3 3H5a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3Z"
    ),
    "gallery_sparkle": (
        "M19 2.5l.7 1.8 1.8.7-1.8.7L19 7.5l-.7-1.8-1.8-.7 1.8-.7L19 2.5Z"
    ),
    # 购物袋（购物车太复古，2026 电商主流是袋子）
    # 主体：圆角梯形袋子；提手：上方两个开口的椭圆环
    "bag_body": (
        "M5.5 7.5h13a1 1 0 0 1 1 1.1l-1 11a3 3 0 0 1-3 2.7H8.5a3 3 0 0 1-3-2.7l-1-11"
        "a1 1 0 0 1 1-1.1Z"
    ),
    "bag_handle": (
        # 两根上提把：M 起点-上弧到右-下，右把对称
        "M9 7.5V6a3 3 0 0 1 6 0v1.5a1 1 0 1 1-2 0V6a1 1 0 0 0-2 0v1.5a1 1 0 1 1-2 0Z"
    ),
    # 用户：饱满的圆头 + 圆滑斜肩
    "mine_head": "M12 4a4 4 0 1 1 0 8 4 4 0 0 1 0-8Z",
    "mine_body": "M4 20.4c0-3.5 3.6-6.4 8-6.4s8 2.9 8 6.4a1.6 1.6 0 0 1-1.6 1.6H5.6A1.6 1.6 0 0 1 4 20.4Z",
}


def make_svg(color: str, *, parts: list[str]) -> bytes:
    paths = "\n".join(f'<path d="{p}" fill="{color}"/>' for p in parts)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
{paths}
</svg>""".encode("utf-8")


ICONS = {
    "home":   ["home"],
    "gallery": ["gallery_card_back", "gallery_card_front", "gallery_sparkle"],
    "cart":    ["bag_body", "bag_handle"],
    "mine":    ["mine_head", "mine_body"],
}


def render(svg_bytes: bytes, out_path: str, size: int = 60) -> None:
    drawing = svg2rlg(io.BytesIO(svg_bytes))
    # Scale 24 → size keeping aspect ratio
    scale = size / 24
    drawing.width *= scale
    drawing.height *= scale
    drawing.scale(scale, scale)
    renderPM.drawToFile(drawing, out_path, fmt="PNG", dpi=72)


def main() -> int:
    for name, parts in ICONS.items():
        for label, color in (("", NORMAL), ("-active", SELECTED)):
            svg = make_svg(color, parts=[ICON_PATHS[p] for p in parts])
            out = os.path.join(ROOT, f"{name}{label}.png")
            render(svg, out)
            print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
