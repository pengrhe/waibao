from __future__ import annotations
import json
import logging
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Dict, List

from jinja2 import Environment, FileSystemLoader

from config import TEMPLATES_DIR, OUTPUT_DIR
from database import get_articles_by_date

logger = logging.getLogger(__name__)

CATEGORY_ORDER = [
    "官方监管与行业协会平台",
    "知识产权领域权威网站",
    "知识产权领域权威数据源",
    "行业核心数据库",
    "学术评价体系数据源",
    "产业链垂直数据源",
    "数字出版细分领域数据源",
    "出版行业权威公众号",
    "知识产权领域权威公众号",
]


def generate_news_page(content_date: str, report_date: str | None = None) -> Path | None:
    """生成新闻日报页面。

    Args:
        content_date: 文章内容日期（爬取目标日期，如昨天）
        report_date:  日报发布日期（文件名和标题用，默认 = content_date 的后一天）
    """
    from datetime import datetime, timedelta

    if report_date is None:
        dt = datetime.strptime(content_date, "%Y-%m-%d") + timedelta(days=1)
        report_date = dt.strftime("%Y-%m-%d")

    articles = get_articles_by_date(content_date)

    categories: dict[str, list] = OrderedDict()
    for cat in CATEGORY_ORDER:
        cat_articles = [a for a in articles if a["source_category"] == cat]
        if cat_articles:
            categories[cat] = cat_articles

    uncategorized = [a for a in articles if a["source_category"] not in CATEGORY_ORDER]
    if uncategorized:
        categories["其他"] = uncategorized

    sources = set(a["source_name"] for a in articles)

    audio_filename = ""
    timeline_json = "[]"
    if articles:
        try:
            from tts_generator import generate_tts
            mp3_path = OUTPUT_DIR / f"news_{report_date}.mp3"
            timeline = generate_tts(report_date, categories, len(articles), mp3_path)
            audio_filename = f"news_{report_date}.mp3"
            timeline_json = json.dumps(timeline, ensure_ascii=False)
        except Exception:
            logger.exception("TTS generation failed, HTML will have no audio")

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("news_digest.html")

    html_content = template.render(
        date=report_date,
        total_count=len(articles),
        source_count=len(sources),
        category_count=len(categories),
        categories=categories,
        audio_url=audio_filename,
        timeline_json=timeline_json,
    )

    output_path = OUTPUT_DIR / f"news_{report_date}.html"
    output_path.write_text(html_content, encoding="utf-8")

    logger.info(f"Generated HTML: {output_path} ({len(articles)} articles, content from {content_date})")
    return output_path
