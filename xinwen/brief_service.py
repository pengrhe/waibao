"""简报计算与落盘：定时任务生成 HTML 后立刻算好并保存，API 优先读缓存。"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from config import OUTPUT_DIR, PUBLIC_BASE_URL
from ai_summary import try_llm_key_summary_body
from brief_formatter import build_wechat_brief_text, full_public_url

logger = logging.getLogger(__name__)


def brief_snapshot_path(report_date: str) -> Path:
    return OUTPUT_DIR / f"brief_{report_date}.json"


def build_digest_outline(articles: list[dict]) -> str:
    lines: list[str] = []
    for i, a in enumerate(articles, 1):
        src = a.get("source_name") or ""
        title = (a.get("title") or "").strip()
        summ = (a.get("summary") or "").strip()
        lines.append(f"{i}. 【{src}】{title}")
        if summ:
            short = summ[:200] + ("…" if len(summ) > 200 else "")
            lines.append(f"   {short}")
    return "\n".join(lines) if lines else ""


def compute_brief_response(
    articles: list[dict],
    report_date: str,
    content_date: str,
    html_file: Path,
) -> dict[str, Any]:
    """与 GET /api/news/today/brief 返回结构一致（不含 saved_at）。"""
    html_url = ""
    if html_file.exists():
        html_url = f"/output/news_{report_date}.html"

    report_file = OUTPUT_DIR / f"report_{report_date}.html"
    report_url = f"/output/report_{report_date}.html" if report_file.exists() else ""

    brief_items: list[dict] = []
    for a in articles:
        brief_items.append(
            {
                "title": a.get("title", ""),
                "summary": (a.get("summary") or "")[:500],
                "url": a.get("url", ""),
                "source_name": a.get("source_name", ""),
                "source_category": a.get("source_category", ""),
                "publish_date": a.get("publish_date", ""),
            }
        )

    sources = set(a["source_name"] for a in articles if a.get("source_name"))
    categories: dict[str, int] = {}
    for a in articles:
        c = a.get("source_category") or "其他"
        categories[c] = categories.get(c, 0) + 1

    key_body, key_src = try_llm_key_summary_body(
        articles,
        report_date,
        html_file if html_file.exists() else None,
    )
    wechat_brief = build_wechat_brief_text(
        articles,
        report_date,
        html_url,
        PUBLIC_BASE_URL,
        key_summary_body=key_body,
        report_url_path=report_url,
    )
    full_html_url = full_public_url(PUBLIC_BASE_URL, html_url)
    full_report_url = full_public_url(PUBLIC_BASE_URL, report_url) if report_url else ""

    return {
        "report_date": report_date,
        "content_date": content_date,
        "html_url": html_url,
        "full_html_url": full_html_url,
        "report_url": report_url,
        "full_report_url": full_report_url,
        "html_exists": html_file.exists(),
        "report_exists": report_file.exists(),
        "article_count": len(articles),
        "source_count": len(sources),
        "categories": categories,
        "digest_outline": build_digest_outline(articles),
        "wechat_brief": wechat_brief,
        "key_summary": key_body,
        "key_summary_source": key_src,
        "articles": brief_items,
    }


def save_brief_snapshot(
    report_date: str,
    content_date: str,
    articles: list[dict],
    html_file: Path,
) -> Path | None:
    """爬取结束后调用：生成简报 JSON（含 LLM 摘要），供 7 点 RPA 直接读。"""
    try:
        payload = compute_brief_response(articles, report_date, content_date, html_file)
        path = brief_snapshot_path(report_date)
        out = {
            **payload,
            "brief_saved_at": datetime.now().isoformat(timespec="seconds"),
        }
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"Brief snapshot saved: {path}")
        return path
    except Exception:
        logger.exception("Failed to save brief snapshot")
        return None


def load_brief_snapshot(report_date: str) -> dict[str, Any] | None:
    path = brief_snapshot_path(report_date)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        logger.warning("Corrupt brief snapshot, will recompute: %s", path)
        return None


def apply_dynamic_public_url(payload: dict[str, Any]) -> dict[str, Any]:
    """读取缓存后刷新 full_html_url / full_report_url（PUBLIC_BASE_URL 可能事后改过）。"""
    payload = dict(payload)
    html_url = payload.get("html_url") or ""
    payload["full_html_url"] = full_public_url(PUBLIC_BASE_URL, html_url)
    report_url = payload.get("report_url") or ""
    payload["full_report_url"] = full_public_url(PUBLIC_BASE_URL, report_url) if report_url else ""
    return payload
