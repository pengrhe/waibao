"""微信群发风格的纯文本简报（与 HTML 分类顺序一致）。"""
from __future__ import annotations
import re
from collections import OrderedDict

from html_generator import CATEGORY_ORDER

CN_NUM = [
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一", "十二", "十三", "十四", "十五",
]


def group_articles_by_category(articles: list[dict]) -> OrderedDict[str, list]:
    categories: OrderedDict[str, list] = OrderedDict()
    for cat in CATEGORY_ORDER:
        cat_arts = [a for a in articles if a.get("source_category") == cat]
        if cat_arts:
            categories[cat] = cat_arts
    uncategorized = [a for a in articles if a.get("source_category") not in CATEGORY_ORDER]
    if uncategorized:
        categories["其他"] = uncategorized
    return categories


def format_source_for_brief(source_name: str) -> str:
    s = (source_name or "").strip()
    if s.startswith("公众号·"):
        return f"来源: 公众号-{s[len('公众号·'):]}"
    if s.startswith("公众号:"):
        rest = s[len("公众号:") :].strip()
        return f"来源: 公众号-{rest}"
    return f"来源: {s}" if s else "来源: 未知"


def build_key_summary(articles: list[dict], grouped: OrderedDict[str, list]) -> str:
    n = len(articles)
    cats = list(grouped.keys())
    cat_join = "、".join(cats) if cats else "多领域"
    blob = " ".join(
        (a.get("title") or "") + " " + (a.get("summary") or "") for a in articles
    )
    themes: list[str] = []
    if re.search(r"专利|知识产权|SEP|无效|复审|口审", blob):
        themes.append("知识产权与专利程序")
    if re.search(r"出版|图书|码洋|开卷|零售", blob):
        themes.append("出版与市场数据")
    if re.search(r"版权|WTO|诉讼|巴西|争端", blob):
        themes.append("涉外规则与深度研判")
    theme_part = ""
    if themes:
        theme_part = "重点关注" + "、".join(dict.fromkeys(themes)) + "。"
    return (
        f"关键摘要: 本期共{n}条资讯，涵盖{cat_join}。{theme_part}"
        f"建议点击文末链接查看完整排版与语音播报。"
    )


def full_public_url(public_base_url: str, html_url_path: str) -> str:
    base = (public_base_url or "").strip().rstrip("/")
    path = (html_url_path or "").strip()
    if not path:
        return ""
    if not path.startswith("/"):
        path = "/" + path
    if base:
        return base + path
    return path


def build_wechat_brief_text(
    articles: list[dict],
    report_date: str,
    html_url_path: str,
    public_base_url: str,
    key_summary_body: str | None = None,
    report_url_path: str | None = None,
) -> str:
    """
    微信推送卡片样式：
    标题 → 日期 → 状态 → 简报概要（LLM 摘要） → 访问链接 → 签名
    优先链接到叙事式简报 report_，其次 news_ 文章列表。
    """
    if report_url_path:
        link = full_public_url(public_base_url, report_url_path)
    else:
        link = full_public_url(public_base_url, html_url_path)
    title = f"知识产权和出版行业简报（{report_date}）"

    if not articles:
        lines = [
            title,
            f"日期：{report_date}",
            "状态：暂无数据",
            "简报概要：本期暂无收录资讯。",
        ]
        if link:
            lines.extend(["访问链接", link])
        return "\n".join(lines)

    if key_summary_body and key_summary_body.strip():
        summary = key_summary_body.strip()
    else:
        grouped = group_articles_by_category(articles)
        summary = build_key_summary(articles, grouped)

    lines: list[str] = [
        title,
        f"日期：{report_date}",
        "状态：已生成",
        f"简报概要：{summary}",
    ]
    if link:
        lines.extend(["访问链接", link])

    return "\n".join(lines)
