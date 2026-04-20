"""世界知识产权组织 WIPO www.wipo.int"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)


class WipoCrawler(BaseCrawler):
    name = "WIPO世界知识产权组织"
    base_url = "https://www.wipo.int"
    category = "知识产权领域权威数据源"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        news_url = "https://www.wipo.int/pressroom/zh/index.html"
        html = self.fetch(news_url)
        if not html:
            logger.warning(f"[{self.name}] Failed to fetch {news_url}")
            return articles

        soup = self.make_soup(html)
        items = soup.select("div.news-item, li.news-item, article, div.search-result, ul.news-list li")

        for item in items:
            try:
                link = item.select_one("a")
                if not link:
                    continue
                href = link.get("href", "")
                if not href:
                    continue

                title = self.clean_text(link.get_text())
                if not title or len(title) < 4:
                    continue

                pub_date = None
                date_el = item.select_one("time, span.date, .news-date")
                if date_el:
                    dt_attr = date_el.get("datetime", "")
                    if dt_attr:
                        pub_date = dt_attr[:10]
                    else:
                        m = re.search(r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})', date_el.get_text())
                        if m:
                            pub_date = m.group(1)

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
