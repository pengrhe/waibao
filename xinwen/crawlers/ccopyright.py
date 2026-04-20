"""中国版权保护中心 www.ccopyright.com.cn"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "https://www.ccopyright.com.cn/index.php?optionid=998",  # 中心公告
    "https://www.ccopyright.com.cn/index.php?optionid=999",  # 要闻动态
]


class CcopyrightCrawler(BaseCrawler):
    name = "中国版权保护中心"
    base_url = "https://www.ccopyright.com.cn"
    category = "知识产权领域权威网站"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        target_day = f"{target_date.day:02d}"
        target_ym = target_date.strftime("%Y-%m")
        articles = []

        for list_url in LIST_URLS:
            html = self.fetch(list_url)
            if not html:
                continue

            soup = self.make_soup(html)
            items = soup.select("div.ST08 div.core, div.newsArea div.core")
            logger.info(f"[{self.name}] Found {len(items)} items on {list_url}")

            for item in items:
                try:
                    day_el = item.select_one("span.daytime")
                    ym_el = item.select_one("span.yeartime")

                    if day_el and ym_el:
                        day = day_el.get_text().strip()
                        ym = ym_el.get_text().strip()
                        pub_date = f"{ym}-{int(day):02d}"
                    else:
                        pub_date = None

                    if pub_date and pub_date != target_str:
                        continue

                    link = item.select_one("h4 a, div.content h4 a, a.mess, a")
                    if not link:
                        continue

                    href = link.get("href", "")
                    if not href:
                        continue

                    url = href if href.startswith("http") else self.abs_url(href)
                    title = self.clean_text(link.get_text())
                    if not title:
                        title_el = item.select_one("h4")
                        if title_el:
                            title = self.clean_text(title_el.get_text())

                    if not title:
                        continue

                    summary = ""
                    summary_el = item.select_one("a.mess, p.mess, div.mess")
                    if summary_el:
                        summary = self.clean_text(summary_el.get_text())[:500]

                    if not pub_date:
                        continue

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
