"""国家新闻出版署 www.nppa.gov.cn"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "https://www.nppa.gov.cn/xxfb/tzgs/",       # 通知公示
    "https://www.nppa.gov.cn/xxfb/xwfb/",        # 新闻发布
]


class NppaCrawler(BaseCrawler):
    name = "国家新闻出版署"
    base_url = "https://www.nppa.gov.cn"
    category = "官方监管与行业协会平台"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        for list_url in LIST_URLS:
            html = self.fetch(list_url)
            if not html:
                continue

            soup = self.make_soup(html)
            items = soup.select("ul.m2nrul > li")
            logger.info(f"[{self.name}] Found {len(items)} items on {list_url}")

            for li in items:
                try:
                    date_span = li.select_one("span")
                    if not date_span:
                        continue
                    date_text = date_span.get_text().strip().strip("[]")
                    if date_text != target_str:
                        continue

                    link = li.select_one("a")
                    if not link:
                        continue
                    href = link.get("href", "")
                    url = self.abs_url(href) if not href.startswith("http") else href
                    if not href.startswith("http"):
                        url = list_url.rstrip("/") + "/" + href.lstrip("./")

                    # Title might be in JS: var _docTitle = '...'
                    title = self.clean_text(link.get_text())

                    if not title:
                        scripts = li.select("script")
                        for s in scripts:
                            m = re.search(r"_docTitle\s*=\s*['\"](.+?)['\"]", s.string or "")
                            if m:
                                title = m.group(1)
                                break

                    if not title:
                        self.delay()
                        detail_html = self.fetch(url)
                        if detail_html:
                            m = re.search(r"_docTitle\s*=\s*['\"](.+?)['\"]", detail_html)
                            if m:
                                title = m.group(1)
                            else:
                                dsoup = self.make_soup(detail_html)
                                title_el = dsoup.select_one("title")
                                if title_el:
                                    title = self.clean_text(title_el.get_text())

                    if not title:
                        continue

                    summary = ""
                    self.delay()
                    detail_html = self.fetch(url)
                    if detail_html:
                        dsoup = self.make_soup(detail_html)
                        content = dsoup.select_one("#zoom, .pages_content, .TRS_Editor")
                        if content:
                            summary = self.clean_text(content.get_text())[:500]

                    articles.append(Article(
                        url=url,
                        title=title,
                        summary=summary,
                        source_name=self.name,
                        source_category=self.category,
                        publish_date=target_str,
                    ))
                except Exception as e:
                    logger.warning(f"[{self.name}] Error parsing item: {e}")

        return articles
