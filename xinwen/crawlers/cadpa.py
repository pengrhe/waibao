"""中国音像与数字出版协会 www.cadpa.org.cn"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "https://www.cadpa.org.cn/3266/index.html",  # 行业动态
    "https://www.cadpa.org.cn/3265/index.html",  # 通知公告
    "https://www.cadpa.org.cn/3269/index.html",  # 协会动态
]


class CadpaCrawler(BaseCrawler):
    name = "中国音像与数字出版协会"
    base_url = "https://www.cadpa.org.cn"
    category = "数字出版细分领域数据源"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        for list_url in LIST_URLS:
            html = self.fetch(list_url)
            if not html:
                continue

            soup = self.make_soup(html)
            items = soup.select("ul.first_list > li")
            logger.info(f"[{self.name}] Found {len(items)} items on {list_url}")

            for li in items:
                try:
                    link = li.select_one("a")
                    if not link:
                        continue

                    time_span = li.select_one("span.time")
                    pub_date = None
                    if time_span:
                        pub_date = time_span.get_text().strip()

                    if pub_date and pub_date != target_str:
                        continue

                    href = link.get("href", "")
                    if not href:
                        continue
                    url = href if href.startswith("http") else self.abs_url(href)

                    title = link.get("title", "") or self.clean_text(link.get_text())
                    if not title:
                        continue

                    summary = ""
                    self.delay()
                    detail = self.fetch(url)
                    if detail:
                        dsoup = self.make_soup(detail)
                        content = dsoup.select_one("div.content, div.article_content, .TRS_Editor")
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
                    logger.warning(f"[{self.name}] Error: {e}")

        return articles
