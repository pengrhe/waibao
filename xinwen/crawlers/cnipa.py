"""国家知识产权局 www.cnipa.gov.cn"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "https://www.cnipa.gov.cn/col/col53/index.html",  # 局要闻
    "https://www.cnipa.gov.cn/col/col74/index.html",  # 通知公告
]


class CnipaCrawler(BaseCrawler):
    name = "国家知识产权局"
    base_url = "https://www.cnipa.gov.cn"
    category = "知识产权领域权威网站"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        for list_url in LIST_URLS:
            html = self.fetch(list_url)
            if not html:
                continue

            # CNIPA uses CDATA records in datastore XML blocks
            cdata_articles = self._parse_cdata(html, target_str, list_url)
            articles.extend(cdata_articles)

            # Also try standard list parsing
            soup = self.make_soup(html)
            for li in soup.select("ul.list li, ul.list.clearfix li, ul.list.fl li"):
                try:
                    link = li.select_one("a")
                    if not link:
                        continue
                    href = link.get("href", "")
                    if not href:
                        continue

                    date_span = li.select_one("span.fr, span")
                    pub_date = None
                    if date_span:
                        m = re.search(r'(\d{4}-\d{2}-\d{2})', date_span.get_text())
                        if m:
                            pub_date = m.group(1)

                    if pub_date and pub_date != target_str:
                        continue

                    url = href if href.startswith("http") else self.abs_url(href)
                    title = self.clean_text(link.get_text())
                    if not title:
                        continue

                    if not pub_date:
                        m = re.search(r'/art/(\d{4})/(\d{1,2})/(\d{1,2})/', href)
                        if m:
                            pub_date = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

                    if pub_date != target_str:
                        continue

                    summary = self._fetch_summary(url)

                    articles.append(Article(
                        url=url,
                        title=title,
                        summary=summary,
                        source_name=self.name,
                        source_category=self.category,
                        publish_date=target_str,
                    ))
                except Exception as e:
                    logger.warning(f"[{self.name}] Error parsing li: {e}")

        return articles

    def _parse_cdata(self, html: str, target_str: str, list_url: str) -> list[Article]:
        results = []
        cdata_blocks = re.findall(r'<!\[CDATA\[(.*?)\]\]>', html, re.DOTALL)
        for block in cdata_blocks:
            from bs4 import BeautifulSoup
            bsoup = BeautifulSoup(block, "lxml")
            link = bsoup.select_one("a")
            if not link:
                continue
            href = link.get("href", "")
            if not href:
                continue
            title = self.clean_text(link.get_text())
            if not title:
                continue

            date_span = bsoup.select_one("span")
            pub_date = None
            if date_span:
                m = re.search(r'(\d{4}-\d{2}-\d{2})', date_span.get_text())
                if m:
                    pub_date = m.group(1)

            if not pub_date:
                m = re.search(r'/art/(\d{4})/(\d{1,2})/(\d{1,2})/', href)
                if m:
                    pub_date = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"

            if pub_date != target_str:
                continue

            url = href if href.startswith("http") else self.abs_url(href)
            summary = self._fetch_summary(url)

            results.append(Article(
                url=url,
                title=title,
                summary=summary,
                source_name=self.name,
                source_category=self.category,
                publish_date=target_str,
            ))
        return results

    def _fetch_summary(self, url: str) -> str:
        self.delay()
        detail = self.fetch(url)
        if not detail:
            return ""
        dsoup = self.make_soup(detail)
        content = dsoup.select_one("#zoom, .article_content, .TRS_Editor, .content-con")
        if content:
            return self.clean_text(content.get_text())[:500]
        return ""
