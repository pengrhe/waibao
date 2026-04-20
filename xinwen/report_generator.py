"""叙事式简报 HTML 生成器：调用 LLM 生成分章节 Markdown，渲染为 HTML 页面。"""
from __future__ import annotations
import logging
from pathlib import Path

import markdown
from jinja2 import Environment, FileSystemLoader

from config import TEMPLATES_DIR, OUTPUT_DIR
from database import get_articles_by_date
from ai_summary import try_llm_full_report

logger = logging.getLogger(__name__)


def generate_report_page(
    content_date: str,
    report_date: str | None = None,
    articles: list[dict] | None = None,
) -> Path | None:
    """生成叙事式简报 HTML（report_{date}.html）。

    Args:
        content_date: 文章内容日期
        report_date:  简报发布日期（文件名用），默认 content_date 后一天
        articles:     可选，直接传入文章列表避免重复查库
    """
    from datetime import datetime, timedelta

    if report_date is None:
        dt = datetime.strptime(content_date, "%Y-%m-%d") + timedelta(days=1)
        report_date = dt.strftime("%Y-%m-%d")

    if articles is None:
        articles = get_articles_by_date(content_date)

    if not articles:
        logger.warning("No articles for %s, skip report generation", content_date)
        return None

    html_path = OUTPUT_DIR / f"news_{report_date}.html"
    md_text = try_llm_full_report(articles, report_date, html_path if html_path.exists() else None)

    if not md_text:
        logger.warning("LLM full report returned empty, skip HTML generation")
        return None

    report_html = markdown.markdown(
        md_text,
        extensions=["tables", "fenced_code"],
        output_format="html",
    )

    audio_url = ""
    report_mp3 = OUTPUT_DIR / f"report_{report_date}.mp3"
    try:
        from tts_generator import generate_report_tts
        if generate_report_tts(report_date, md_text, report_mp3):
            audio_url = f"report_{report_date}.mp3"
    except Exception:
        logger.exception("Report TTS failed, page will have no audio")

    if not audio_url:
        news_mp3 = OUTPUT_DIR / f"news_{report_date}.mp3"
        if news_mp3.exists():
            audio_url = f"news_{report_date}.mp3"

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template("report_brief.html")

    page_html = template.render(
        date=report_date,
        report_html=report_html,
        audio_url=audio_url,
        news_url=f"news_{report_date}.html",
    )

    output_path = OUTPUT_DIR / f"report_{report_date}.html"
    output_path.write_text(page_html, encoding="utf-8")
    logger.info("Generated report: %s (%d articles)", output_path, len(articles))

    md_path = OUTPUT_DIR / f"report_{report_date}.md"
    md_path.write_text(md_text, encoding="utf-8")

    return output_path
