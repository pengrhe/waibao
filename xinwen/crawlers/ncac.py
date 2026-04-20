"""国家版权局 www.ncac.gov.cn"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "https://www.ncac.gov.cn/xxfb/ywxx/",  # 要闻信息
    "https://www.ncac.gov.cn/xxfb/tzgg/",  # 通知公告
]


class NcacCrawler(BaseCrawler):
    name = "国家版权局"
    base_url = "https://www.ncac.gov.cn"
    category = "知识产权领域权威网站"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        articles = []

        for list_url in LIST_URLS:
            html = self.fetch(list_url)
            if not html:
                continue

            soup = self.make_soup(html)
            items = soup.select("ul.m2nrul > li, ul.list_con li, ul.m2newsList li, div.list_right_nr ul li")
            logger.info(f"[{self.name}] Found {len(items)} items on {list_url}")

            for li in items:
                try:
                    link = li.select_one("a")
                    if not link:
                        continue
                    href = link.get("href", "")
                    if not href:
                        continue

                    date_span = li.select_one("span")
                    pub_date = None
                    if date_span:
                        m = re.search(r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})', date_span.get_text())
                        if m:
                            pub_date = m.group(1)

                    if not pub_date:
                        m = re.search(r'/(\d{4})(\d{2})/t(\d{8})_', href)
                        if m:
                            raw = m.group(3)
                            pub_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:8]}"

                    if pub_date and pub_date != target_str:
                        continue

                    if href.startswith("http"):
                        url = href
                    elif href.startswith("./"):
                        url = list_url.rstrip("/") + "/" + href.lstrip("./")
                    else:
                        url = self.abs_url(href)

                    title = self.clean_text(link.get_text())

                    if not title:
                        scripts = li.select("script")
                        for s in scripts:
                            if s.string:
                                m = re.search(r"_docTitle\s*=\s*['\"](.+?)['\"]", s.string)
                                if m:
                                    title = m.group(1)

                    if not title:
                        continue

                    summary = ""
                    if pub_date == target_str or not pub_date:
                        self.delay()
                        detail_html = self.fetch(url)
                        if detail_html:
                            dsoup = self.make_soup(detail_html)
                            if not pub_date:
                                date_el = dsoup.select_one("span.article_date, .article-info, .info-date")
                                if date_el:
                                    m2 = re.search(r'(\d{4}-\d{2}-\d{2})', date_el.get_text())
                                    if m2:
                                        pub_date = m2.group(1)
                            if pub_date != target_str:
                                continue
                            content = dsoup.select_one(".TRS_Editor, .article_content, #zoom, .text_con")
                            if content:
                                summary = self.clean_text(content.get_text())[:500]

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
