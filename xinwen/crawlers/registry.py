from __future__ import annotations
import logging
from crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)

_registry: dict[str, BaseCrawler] = {}


def register(crawler: BaseCrawler):
    _registry[crawler.name] = crawler
    logger.info(f"Registered crawler: {crawler.name}")


def get_all() -> dict[str, BaseCrawler]:
    return dict(_registry)


def get(name: str) -> BaseCrawler | None:
    return _registry.get(name)
