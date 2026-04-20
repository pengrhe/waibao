"""7:00 scheduled job: fetch today's brief and send to WeChat."""
from __future__ import annotations
import logging
import requests

from config import WECHAT_BRIEF_API, WECHAT_SEND_TO, PROXY

logger = logging.getLogger(__name__)


def send_daily_brief():
    logger.info("[WeChat] Fetching brief from %s", WECHAT_BRIEF_API)
    try:
        resp = requests.get(WECHAT_BRIEF_API, timeout=30, proxies={"http": PROXY, "https": PROXY})
        resp.raise_for_status()
        data = resp.json()
    except Exception:
        logger.exception("[WeChat] Failed to fetch brief API")
        return

    text = data.get("wechat_brief") or ""
    if not text:
        logger.warning("[WeChat] wechat_brief is empty, skip sending")
        return

    try:
        from shanxiang_wechat import WeChat
        wechat = WeChat()
        wechat.send(WECHAT_SEND_TO, text)
        logger.info("[WeChat] Sent brief to '%s' (%d chars)", WECHAT_SEND_TO, len(text))
    except Exception:
        logger.exception("[WeChat] Failed to send via WeChat")
