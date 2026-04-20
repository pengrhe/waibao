"""中国音像著作权集体管理协会 www.cavca.org"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)


class CavcaCrawler(BaseCrawler):
    name = "中国音像著作权集体管理协会"
    base_url = "http://www.cavca.org"
    category = "知识产权领域权威数据源"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        list_urls = [
            "https://www.cavca.org/news/8",   # 协会新闻
            "https://www.cavca.org/news/22",  # 协会公告
            "https://www.cavca.org/news/9",   # 行业动态
        ]

        for list_url in list_urls:
            html = self.fetch(list_url)
            if not html:
                logger.warning(f"[{self.name}] Failed to fetch {list_url}")
                continue

            soup = self.make_soup(html)
            items = soup.select("ul li, div.list li, ul.news_list li")

            for li in items:
                try:
                    link = li.select_one("a")
                    if not link:
                        continue
                    href = link.get("href", "")
                    if not href or href == "#":
                        continue
                    title = self.clean_text(link.get_text())
                    if not title or len(title) < 4:
                        continue

                    pub_date = None
                    date_span = li.select_one("span, em, time")
                    if date_span:
                        m = re.search(r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})', date_span.get_text())
                        if m:
                            pub_date = re.sub(r'[/.]', '-', m.group(1))

                    if not pub_date:
                        m = re.search(r'/(\d{4})[-/]?(\d{2})[-/]?(\d{2})', href)
                        if m:
                            pub_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

                    if pub_date and pub_date != target_str:
                        continue
                    if not pub_date:
                        continue

                    url = href if href.startswith("http") else self.abs_url(href)

                    articles.append(Article(
                        url=url,
                        title=title,
                        summary="",
                        source_name=self.name,
                        source_category=self.category,
                        publish_date=target_str,
                    ))
                except Exception as e:
                    logger.warning(f"[{self.name}] Error: {e}")

        return articles
