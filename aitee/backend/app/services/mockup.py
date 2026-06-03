"""商品底图（mockup）SVG 生成。

与 frontend `src/utils/placeholder.ts` 的 tshirtMockup / toteMockup 视觉一致，
作为后端唯一出处：C 端按当前颜色 / 正反面向 `/products/{id}/mockup` 请求底图，
不再在各端各自写死 CSS / SVG。
"""
from __future__ import annotations

# 颜色名 -> hex。与 frontend colorBg() 保持一致；同时兼容中文名与直接传入的 hex。
COLOR_MAP: dict[str, str] = {
    # 英文（后端 sku.color 用）
    "white": "#ffffff",
    "black": "#1f2937",
    "gray": "#9ca3af",
    "grey": "#9ca3af",
    "red": "#ef4444",
    "pink": "#f9a8d4",
    "blue": "#3b82f6",
    "green": "#22c55e",
    "yellow": "#facc15",
    "orange": "#fb923c",
    "purple": "#a855f7",
    "brown": "#92400e",
    "natural": "#f5f1ea",
    "khaki": "#d4c5a0",
    # 中文别名
    "白": "#ffffff",
    "黑": "#1f2937",
    "灰": "#9ca3af",
    "红": "#ef4444",
    "粉": "#f9a8d4",
    "蓝": "#3b82f6",
    "绿": "#22c55e",
    "黄": "#facc15",
    "橙": "#fb923c",
    "紫": "#a855f7",
    "棕": "#92400e",
    "米白": "#f5f1ea",
    "卡其": "#d4c5a0",
}


def resolve_color(color: str | None) -> str:
    """把颜色名 / 中文名 / hex 统一解析为 #rrggbb。无法识别时回退白色。"""
    if not color:
        return "#ffffff"
    c = color.strip()
    if c.startswith("#"):
        return c
    key = c.lower()
    if key in COLOR_MAP:
        return COLOR_MAP[key]
    # 中文名可能是「深灰」「米白」这类包含关系
    for name, hex_val in COLOR_MAP.items():
        if name in c:
            return hex_val
    return "#ffffff"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    v = hex_color.lstrip("#")
    if len(v) == 3:
        v = "".join(ch * 2 for ch in v)
    try:
        num = int(v, 16)
    except ValueError:
        num = 0xFFFFFF
    return (num >> 16) & 0xFF, (num >> 8) & 0xFF, num & 0xFF


def _is_light(hex_color: str) -> bool:
    r, g, b = _hex_to_rgb(hex_color)
    return (r * 299 + g * 587 + b * 114) / 1000 > 200


def _darken(hex_color: str, amount: float) -> str:
    r, g, b = _hex_to_rgb(hex_color)

    def f(v: int) -> int:
        return max(0, min(255, round(v * (1 - amount))))

    return f"rgb({f(r)},{f(g)},{f(b)})"


def tshirt_mockup(color: str = "#ffffff", side: str = "front") -> str:
    color = resolve_color(color)
    stroke = "#9ca3af" if _is_light(color) else "#374151"
    shadow = _darken(color, 0.08)
    label = "正面" if side != "back" else "背面"
    label_fill = "#d4d4d8" if _is_light(color) else "rgba(255,255,255,0.4)"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 420">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fafafa"/>
      <stop offset="1" stop-color="#eeeeee"/>
    </linearGradient>
  </defs>
  <rect width="360" height="420" fill="url(#bg)"/>
  <ellipse cx="180" cy="395" rx="120" ry="10" fill="rgba(0,0,0,0.08)"/>
  <path d="M90 90 L140 60 L150 75 Q180 95 210 75 L220 60 L270 90 L300 130 L260 150 L260 380 L100 380 L100 150 L60 130 Z"
    fill="{color}" stroke="{stroke}" stroke-width="1.5" stroke-linejoin="round"/>
  <path d="M150 75 Q180 100 210 75" fill="none" stroke="{stroke}" stroke-width="1.5"/>
  <path d="M90 90 L60 130 L100 150 L100 175 L130 165 L130 130 L120 100 Z" fill="{shadow}" opacity="0.4"/>
  <path d="M270 90 L300 130 L260 150 L260 175 L230 165 L230 130 L240 100 Z" fill="{shadow}" opacity="0.4"/>
  <text x="180" y="230" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="14" font-weight="600"
    fill="{label_fill}" text-anchor="middle">{label}</text>
</svg>"""


def tote_mockup(color: str = "#ffffff") -> str:
    color = resolve_color(color)
    stroke = "#9ca3af" if _is_light(color) else "#374151"
    label_fill = "#d4d4d8" if _is_light(color) else "rgba(255,255,255,0.5)"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 420">
  <rect width="360" height="420" fill="#f5f5f5"/>
  <ellipse cx="180" cy="400" rx="110" ry="8" fill="rgba(0,0,0,0.08)"/>
  <path d="M120 130 Q120 70 150 70 Q180 70 180 100 Q180 130 150 130" fill="none" stroke="{stroke}" stroke-width="3"/>
  <path d="M240 130 Q240 70 210 70 Q180 70 180 100 Q180 130 210 130" fill="none" stroke="{stroke}" stroke-width="3"/>
  <rect x="90" y="130" width="180" height="240" rx="8" fill="{color}" stroke="{stroke}" stroke-width="1.5"/>
  <text x="180" y="260" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="14" font-weight="600"
    fill="{label_fill}" text-anchor="middle">帆布包</text>
</svg>"""


def product_mockup(category_slug: str | None, color: str = "#ffffff", side: str = "front") -> str:
    if category_slug == "tote":
        return tote_mockup(color)
    return tshirt_mockup(color, side)
