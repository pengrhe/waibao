from __future__ import annotations
import re
import logging
from datetime import date, datetime
from typing import Optional, List, Dict
from urllib.parse import urljoin

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)


class GenericCrawler(BaseCrawler):
    """
    Configurable crawler for typical news-list + detail-page pattern.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        category: str,
        list_urls: list[str],
        list_item_selector: str,
        link_attr: str = "href",
        title_selector: str | None = None,
        date_selector: str | None = None,
        date_attr: str | None = None,
        content_selector: str | None = None,
        date_formats: list[str] | None = None,
        encoding: str | None = None,
        detail_title_selector: str | None = None,
        detail_date_selector: str | None = None,
        detail_content_selector: str | None = None,
        needs_detail: bool = True,
    ):
        super().__init__()
        self.name = name
        self.base_url = base_url
        self.category = category
        self.list_urls = list_urls
        self.list_item_selector = list_item_selector
        self.link_attr = link_attr
        self.title_selector = title_selector
        self.date_selector = date_selector
        self.date_attr = date_attr
        self.content_selector = content_selector
        self.date_formats = date_formats or ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日", "%Y.%m.%d"]
        self.encoding = encoding
        self.detail_title_selector = detail_title_selector
        self.detail_date_selector = detail_date_selector
        self.detail_content_selector = detail_content_selector
        self.needs_detail = needs_detail

    def parse_date_str(self, text: str) -> str | None:
        text = text.strip()
        date_match = re.search(r'(\d{4}[-/\.年]\d{1,2}[-/\.月]\d{1,2})', text)
        if date_match:
            raw = date_match.group(1)
            for fmt in self.date_formats:
                try:
                    dt = datetime.strptime(raw, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue
        return None

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        for list_url in self.list_urls:
            html = self.fetch(list_url)
            if not html:
                logger.warning(f"[{self.name}] Failed to fetch list page: {list_url}")
                continue

            soup = self.make_soup(html)
            items = soup.select(self.list_item_selector)
            logger.info(f"[{self.name}] Found {len(items)} items on {list_url}")

            for item in items:
                try:
                    link_el = item if item.name == "a" else item.select_one("a")
                    if not link_el:
                        continue

                    href = link_el.get(self.link_attr, "")
                    if not href:
                        continue
                    url = self.abs_url(href) if not href.startswith("http") else href

                    title = ""
                    if self.title_selector:
                        title_el = item.select_one(self.title_selector)
                        if title_el:
                            title = self.clean_text(title_el.get_text())
                    if not title:
                        title = self.clean_text(link_el.get_text())
                    if not title:
                        continue

                    pub_date = None
                    if self.date_selector:
                        date_el = item.select_one(self.date_selector)
                        if date_el:
                            date_text = date_el.get(self.date_attr) if self.date_attr else date_el.get_text()
                            if date_text:
                                pub_date = self.parse_date_str(date_text)

                    if not pub_date:
                        date_match = re.search(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', href)
                        if date_match:
                            pub_date = f"{date_match.group(1)}-{int(date_match.group(2)):02d}-{int(date_match.group(3)):02d}"

                    if pub_date and pub_date != target_str:
                        continue

                    summary = ""
                    if self.needs_detail:
                        self.delay()
                        detail = self._fetch_detail(url)
                        if detail:
                            if not pub_date:
                                pub_date = detail.get("date")
                            if not title or (detail.get("title") and len(detail["title"]) > len(title)):
                                title = detail["title"]
                            summary = detail.get("summary", "")

                    if pub_date != target_str:
                        continue

                    articles.append(Article(
                        url=url,
                        title=title,
                        summary=summary[:500],
                        source_name=self.name,
                        source_category=self.category,
                        publish_date=target_str,
                    ))

                except Exception as e:
                    logger.warning(f"[{self.name}] Error parsing item: {e}")
                    continue

        return articles

    def _fetch_detail(self, url: str) -> dict | None:
        html = self.fetch(url)
        if not html:
            return None
        soup = self.make_soup(html)
        result = {}

        if self.detail_title_selector:
            el = soup.select_one(self.detail_title_selector)
            if el:
                result["title"] = self.clean_text(el.get_text())

        if self.detail_date_selector:
            el = soup.select_one(self.detail_date_selector)
            if el:
                result["date"] = self.parse_date_str(el.get_text())

        sel = self.detail_content_selector or self.content_selector
        if sel:
            el = soup.select_one(sel)
            if el:
                result["summary"] = self.clean_text(el.get_text())[:500]

        return result if result else None
