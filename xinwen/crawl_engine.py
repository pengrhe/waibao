"""Core crawl orchestrator: runs all crawlers, deduplicates, stores, generates HTML."""
from __future__ import annotations
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Optional, Dict

from crawlers import registry
from database import insert_article, log_crawl, get_articles_by_date
from html_generator import generate_news_page
from report_generator import generate_report_page
from brief_service import save_brief_snapshot

logger = logging.getLogger(__name__)


def run_crawl(target_date: date | None = None) -> dict:
    """
    Run all registered crawlers for target_date (defaults to yesterday).
    Returns summary dict with stats.
    """
    if target_date is None:
        target_date = date.today() - timedelta(days=1)

    target_str = target_date.strftime("%Y-%m-%d")
    crawl_date = date.today().strftime("%Y-%m-%d")

    logger.info(f"=== Starting crawl for {target_str} ===")

    all_crawlers = registry.get_all()
    total_new = 0
    total_dup = 0
    source_count = 0
    errors = []

    for name, crawler in all_crawlers.items():
        logger.info(f"--- Crawling: {name} ---")
        try:
            articles = crawler.crawl(target_date)
            new_count = 0
            dup_count = 0

            for article in articles:
                inserted = insert_article(article, crawl_date)
                if inserted:
                    new_count += 1
                else:
                    dup_count += 1

            total_new += new_count
            total_dup += dup_count
            if new_count > 0:
                source_count += 1

            log_crawl(name, target_str, "success", new_count)
            logger.info(f"[{name}] Done: {new_count} new, {dup_count} duplicates")

        except Exception as e:
            error_msg = str(e)[:500]
            log_crawl(name, target_str, "error", 0, error_msg)
            errors.append(f"{name}: {error_msg}")
            logger.error(f"[{name}] Crawl failed: {e}")

    html_path = generate_news_page(target_str, crawl_date)

    arts_after = get_articles_by_date(target_str) if html_path else []

    report_path = None
    if html_path and arts_after:
        report_path = generate_report_page(target_str, crawl_date, arts_after)

    brief_path_str = None
    if html_path:
        bp = save_brief_snapshot(
            crawl_date,
            target_str,
            arts_after,
            Path(html_path),
        )
        brief_path_str = str(bp) if bp else None

    summary = {
        "target_date": target_str,
        "crawl_date": crawl_date,
        "total_new_articles": total_new,
        "total_duplicates": total_dup,
        "source_count": source_count,
        "crawler_count": len(all_crawlers),
        "errors": errors,
        "html_path": str(html_path) if html_path else None,
        "report_path": str(report_path) if report_path else None,
        "brief_path": brief_path_str,
    }

    logger.info(f"=== Crawl complete: {total_new} new articles from {source_count} sources ===")
    return summary
