from __future__ import annotations
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import (
    CRAWL_SCHEDULE_HOUR,
    CRAWL_SCHEDULE_MINUTE,
    WECHAT_SEND_HOUR,
    WECHAT_SEND_MINUTE,
)

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _daily_crawl_job():
    from crawl_engine import run_crawl
    logger.info("Daily scheduled crawl triggered")
    try:
        summary = run_crawl()
        logger.info(f"Daily crawl complete: {summary}")
    except Exception as e:
        logger.error(f"Daily crawl failed: {e}")


def _daily_wechat_job():
    from wechat_sender import send_daily_brief
    logger.info("Daily WeChat send triggered")
    try:
        send_daily_brief()
    except Exception as e:
        logger.error(f"Daily WeChat send failed: {e}")


def start_scheduler():
    global _scheduler
    _scheduler = BackgroundScheduler(job_defaults={"misfire_grace_time": 600})
    _scheduler.add_job(
        _daily_crawl_job,
        trigger=CronTrigger(hour=CRAWL_SCHEDULE_HOUR, minute=CRAWL_SCHEDULE_MINUTE),
        id="daily_crawl",
        name="每日新闻爬取",
        replace_existing=True,
    )
    _scheduler.add_job(
        _daily_wechat_job,
        trigger=CronTrigger(hour=WECHAT_SEND_HOUR, minute=WECHAT_SEND_MINUTE),
        id="daily_wechat",
        name="每日微信简报推送",
        replace_existing=True,
    )
    _scheduler.start()
    logger.info(
        "Scheduler started: crawl at %02d:%02d, wechat at %02d:%02d",
        CRAWL_SCHEDULE_HOUR, CRAWL_SCHEDULE_MINUTE,
        WECHAT_SEND_HOUR, WECHAT_SEND_MINUTE,
    )


def stop_scheduler():
    global _scheduler
    if _scheduler:
        _scheduler.shutdown()
        logger.info("Scheduler stopped")
