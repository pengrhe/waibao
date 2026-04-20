"""Load data sources from Excel and register all crawlers."""
from __future__ import annotations
import logging

from crawlers import registry
from crawlers.nppa import NppaCrawler
from crawlers.ncac import NcacCrawler
from crawlers.cnipa import CnipaCrawler
from crawlers.ccopyright import CcopyrightCrawler
from crawlers.publishing_org import PublishingOrgCrawler
from crawlers.cadpa import CadpaCrawler
from crawlers.cnipr import CniprCrawler
from crawlers.chinapublish import ChinapublishCrawler
from crawlers.prccopyright import PrccopyrightCrawler
from crawlers.cavca import CavcaCrawler
from crawlers.wipo import WipoCrawler
from crawlers.weixin_tikhub import WeixinTikhubCrawler

logger = logging.getLogger(__name__)

ALL_CRAWLERS = [
    NppaCrawler,
    NcacCrawler,
    CnipaCrawler,
    CcopyrightCrawler,
    PublishingOrgCrawler,
    CadpaCrawler,
    CniprCrawler,
    ChinapublishCrawler,
    PrccopyrightCrawler,
    CavcaCrawler,
    WipoCrawler,
    WeixinTikhubCrawler,
]


def register_all():
    for cls in ALL_CRAWLERS:
        try:
            instance = cls()
            registry.register(instance)
        except Exception as e:
            logger.error(f"Failed to register {cls.__name__}: {e}")

    logger.info(f"Registered {len(registry.get_all())} crawlers")
