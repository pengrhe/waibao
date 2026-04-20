"""中国文字著作权协会 www.prccopyright.org.cn"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "http://www.prccopyright.org.cn/search/Search.aspx?field=id&key=6970db87-9369-4260-9676-76dc2cb4df13&title=%E5%8D%8F%E4%BC%9A%E5%8A%A8%E6%80%81",  # 协会动态
    "http://www.prccopyright.org.cn/search/Search.aspx?key=5ecab3e2-eadf-4911-8843-1ab164f71a6b&field=id&title=%E5%8D%8F%E4%BC%9A%E5%85%AC%E5%91%8A",  # 协会公告
]


class PrccopyrightCrawler(BaseCrawler):
    name = "中国文字著作权协会"
    base_url = "http://www.prccopyright.org.cn"
    category = "知识产权领域权威数据源"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        for list_url in LIST_URLS:
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
                    date_span = li.select_one("span")
                    if date_span:
                        m = re.search(r'(\d{4}[-/.]\d{1,2}[-/.]\d{1,2})', date_span.get_text())
                        if m:
                            pub_date = re.sub(r'[/.]', '-', m.group(1))

                    if not pub_date:
                        m = re.search(r'/(\d{4})(\d{2})\d{2}/|/(\d{8})', href)
                        if m:
                            raw = m.group(3) or (m.group(1) + m.group(2))
                            if len(raw) == 8:
                                pub_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"

                    if pub_date and pub_date != target_str:
                        continue
                    if not pub_date:
                        continue

                    url = href if href.startswith("http") else self.abs_url(href)

                    summary = ""
                    self.delay()
                    detail = self.fetch(url)
                    if detail:
                        dsoup = self.make_soup(detail)
                        content = dsoup.select_one(".article_content, .content, .TRS_Editor, #zoom")
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
