"""中国出版协会 www.publishing.org.cn"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "https://www.publishing.org.cn/zgcbxh/xyxw/",   # 行业新闻
    "https://www.publishing.org.cn/zgcbxh/tzgg/",    # 通知公告
]


class PublishingOrgCrawler(BaseCrawler):
    name = "中国出版协会"
    base_url = "https://www.publishing.org.cn"
    category = "官方监管与行业协会平台"
    encoding = "utf-8"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        for list_url in LIST_URLS:
            html = self.fetch(list_url)
            if not html:
                logger.warning(f"[{self.name}] Failed to fetch {list_url}")
                continue

            soup = self.make_soup(html)
            items = soup.select("ul.list li, ul.news_list li, div.list_content li, ul li")
            logger.info(f"[{self.name}] Found {len(items)} candidate items on {list_url}")

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
                    date_span = li.select_one("span")
                    if date_span:
                        m = re.search(r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})', date_span.get_text())
                        if m:
                            pub_date = re.sub(r'[/.]', '-', m.group(1))

                    if not pub_date:
                        m = re.search(r'/(\d{4})(\d{2})/t?(\d{8})', href)
                        if m:
                            raw = m.group(3)
                            pub_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"

                    if pub_date and pub_date != target_str:
                        continue

                    url = href if href.startswith("http") else self.abs_url(href)

                    if not pub_date:
                        self.delay()
                        detail = self.fetch(url)
                        if detail:
                            m = re.search(r'(\d{4}-\d{2}-\d{2})', detail)
                            if m:
                                pub_date = m.group(1)

                    if pub_date != target_str:
                        continue

                    summary = ""
                    self.delay()
                    detail = self.fetch(url)
                    if detail:
                        dsoup = self.make_soup(detail)
                        content = dsoup.select_one(".TRS_Editor, .article_content, #zoom, .text_con, .content")
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
