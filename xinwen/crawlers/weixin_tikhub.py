"""微信公众号爬虫 - 基于 TikHub 付费 API

使用 TikHub (https://tikhub.io) 的 WeChat MP Web API 获取公众号文章列表。
价格：$0.001/次请求，12 个账号每天仅 ~$0.012。

使用前需要：
1. 注册 tikhub.io 账号并创建 API Token
2. 将 Token 填入 config.py 的 TIKHUB_API_TOKEN 或设置环境变量
3. 在 weixin_accounts.json 中填入每个公众号的原始 ID (ghid)
"""
from __future__ import annotations
import json
import logging
import time
import random
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Optional

import requests

from crawlers.base import BaseCrawler
from database import Article
from config import TIKHUB_API_TOKEN, TIKHUB_API_BASE, PROXIES, BASE_DIR

logger = logging.getLogger(__name__)

ACCOUNTS_FILE = BASE_DIR / "weixin_accounts.json"


def load_accounts() -> List[Dict[str, str]]:
    if not ACCOUNTS_FILE.exists():
        logger.warning(f"[WeixinTikhub] Config file not found: {ACCOUNTS_FILE}")
        return []
    try:
        with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("accounts", [])
    except Exception as e:
        logger.error(f"[WeixinTikhub] Failed to load {ACCOUNTS_FILE}: {e}")
        return []


class WeixinTikhubCrawler(BaseCrawler):
    name = "微信公众号(TikHub)"
    base_url = "https://mp.weixin.qq.com"
    category = ""
    encoding = "utf-8"

    def __init__(self):
        super().__init__()
        self.api_token = TIKHUB_API_TOKEN
        self.api_base = TIKHUB_API_BASE
        self.api_session = requests.Session()
        if "tikhub.dev" not in self.api_base:
            self.api_session.proxies = PROXIES
        if self.api_token:
            self.api_session.headers.update({
                "Authorization": f"Bearer {self.api_token}",
                "Accept": "application/json",
            })

    def crawl(self, target_date: date) -> list[Article]:
        if not self.api_token:
            logger.warning(
                f"[{self.name}] TikHub API Token 未配置！"
                "请设置 TIKHUB_API_TOKEN 环境变量或在 config.py 中配置"
            )
            return []

        accounts = load_accounts()
        configured = [a for a in accounts if a.get("ghid")]
        if not configured:
            logger.warning(
                f"[{self.name}] 没有配置 ghid 的公众号！"
                f"请编辑 {ACCOUNTS_FILE} 填入公众号原始ID"
            )
            return []

        logger.info(f"[{self.name}] {len(configured)}/{len(accounts)} accounts configured")

        target_str = target_date.strftime("%Y-%m-%d")
        all_articles = []

        for account in configured:
            name = account["name"]
            ghid = account["ghid"]
            category = account.get("category", "微信公众号")

            try:
                articles = self._fetch_account_articles(
                    name, ghid, category, target_str, target_date
                )
                all_articles.extend(articles)
                if articles:
                    logger.info(f"[{self.name}] {name}: {len(articles)} articles for {target_str}")
                else:
                    logger.info(f"[{self.name}] {name}: 0 articles for {target_str}")
            except Exception as e:
                logger.warning(f"[{self.name}] Error fetching {name}: {e}")

            time.sleep(random.uniform(0.5, 1.5))

        return all_articles

    def _fetch_account_articles(
        self, account_name: str, ghid: str, category: str,
        target_str: str, target_date: date
    ) -> list[Article]:
        url = f"{self.api_base}/api/v1/wechat_mp/web/fetch_mp_article_list"
        params = {"ghid": ghid, "offset": ""}

        try:
            resp = self.api_session.get(url, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as e:
            logger.warning(f"[{self.name}] API request failed for {account_name}: {e}")
            return []

        if data.get("code") != 200:
            msg = data.get("message_zh") or data.get("message", "Unknown error")
            logger.warning(f"[{self.name}] API error for {account_name}: {msg}")
            return []

        api_data = data.get("data", {})
        article_list = self._extract_articles(api_data)

        articles = []
        for item in article_list:
            try:
                pub_ts = (
                    item.get("send_time")
                    or item.get("create_time")
                    or item.get("update_time", 0)
                )
                if isinstance(pub_ts, str):
                    pub_ts = int(pub_ts)

                if pub_ts:
                    pub_date = datetime.fromtimestamp(pub_ts).date()
                    if pub_date != target_date:
                        continue
                else:
                    continue

                title = (
                    item.get("Title") or item.get("title") or ""
                ).strip()
                if not title:
                    continue

                article_url = (
                    item.get("ContentUrl")
                    or item.get("content_url")
                    or item.get("link")
                    or item.get("url", "")
                )
                if not article_url:
                    continue

                digest = (
                    item.get("Digest")
                    or item.get("digest")
                    or item.get("abstract", "")
                )

                articles.append(Article(
                    url=article_url,
                    title=title,
                    summary=str(digest)[:500],
                    source_name=f"公众号·{account_name}",
                    source_category=category,
                    publish_date=target_str,
                ))
            except Exception as e:
                logger.debug(f"[{self.name}] Parse error for {account_name}: {e}")

        return articles

    def _extract_articles(self, api_data) -> list[dict]:
        """从 TikHub 返回的数据中提取文章列表

        实际返回格式：{"list": [{Title, Digest, ContentUrl, send_time, ...}], "offset": {...}}
        """
        if isinstance(api_data, list):
            return api_data

        if not isinstance(api_data, dict):
            return []

        # TikHub 实际格式：data.list
        for key in ["list", "app_msg_list", "article_list", "articles"]:
            if key in api_data and isinstance(api_data[key], list):
                return api_data[key]

        return []
