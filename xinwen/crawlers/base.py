from __future__ import annotations
import random
import time
import logging
import re
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, List, Dict
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from config import PROXIES, REQUEST_TIMEOUT, MAX_RETRIES, MIN_DELAY, MAX_DELAY, USER_AGENTS
from database import Article

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    name: str = ""
    base_url: str = ""
    category: str = ""
    encoding: str | None = None

    def __init__(self):
        self.session = requests.Session()
        self.session.proxies = PROXIES
        self.session.headers.update({
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })

    def fetch(self, url: str, **kwargs) -> str | None:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
                resp.raise_for_status()
                if self.encoding:
                    resp.encoding = self.encoding
                elif resp.apparent_encoding:
                    resp.encoding = resp.apparent_encoding
                return resp.text
            except Exception as e:
                logger.warning(f"[{self.name}] fetch {url} attempt {attempt} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        return None

    def fetch_json(self, url: str, **kwargs) -> dict | list | None:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self.session.get(url, timeout=REQUEST_TIMEOUT, **kwargs)
                resp.raise_for_status()
                return resp.json()
            except Exception as e:
                logger.warning(f"[{self.name}] fetch_json {url} attempt {attempt} failed: {e}")
                if attempt < MAX_RETRIES:
                    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))
        return None

    def make_soup(self, html: str) -> BeautifulSoup:
        return BeautifulSoup(html, "lxml")

    def abs_url(self, relative: str) -> str:
        return urljoin(self.base_url, relative)

    def delay(self):
        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    def clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    @abstractmethod
    def crawl(self, target_date: date) -> list[Article]:
        """Crawl and return articles published on target_date."""
        ...
