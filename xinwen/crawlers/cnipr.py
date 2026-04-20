"""中国知识产权网 www.cnipr.com"""
from __future__ import annotations
import re
import logging
from datetime import date

from crawlers.base import BaseCrawler
from database import Article

logger = logging.getLogger(__name__)

LIST_URLS = [
    "http://www.cnipr.com/sj/zx/",   # 新闻资讯
]


class CniprCrawler(BaseCrawler):
    name = "中国知识产权网"
    base_url = "http://www.cnipr.com"
    category = "知识产权领域权威网站"

    def crawl(self, target_date: date) -> list[Article]:
        target_str = target_date.strftime("%Y-%m-%d")
        target_mmdd = target_date.strftime("%m-%d")
        articles = []

        for list_url in LIST_URLS:
            html = self.fetch(list_url)
            if not html:
                continue

            soup = self.make_soup(html)
            items = soup.select("li.zx_cont_list1, li.zx_cont_list3")
            logger.info(f"[{self.name}] Found {len(items)} items on {list_url}")

            for li in items:
                try:
                    link = li.select_one("a")
                    if not link:
                        continue
                    href = link.get("href", "")
                    if not href:
                        continue

                    # Date from URL pattern ./YYYYMM/tYYYYMMDD_ID.html
                    pub_date = None
                    m = re.search(r't(\d{4})(\d{2})(\d{2})_', href)
                    if m:
                        pub_date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"

                    if not pub_date:
                        time_div = li.select_one("div.time, div.list1_dongtai_time")
                        if time_div:
                            mm_dd = time_div.get_text().strip()
                            if mm_dd == target_mmdd:
                                pub_date = target_str

                    if pub_date and pub_date != target_str:
                        continue

                    url = href if href.startswith("http") else list_url.rstrip("/") + "/" + href.lstrip("./")

                    title_el = li.select_one("p.list1_title, a p.list1_title")
                    title = self.clean_text(title_el.get_text()) if title_el else self.clean_text(link.get_text())
                    if not title:
                        continue

                    summary = ""
                    summary_el = li.select_one("p.list1_zhaiyao")
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
                    logger.warning(f"[{self.name}] Error: {e}")

        return articles
