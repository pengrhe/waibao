"""一次性脚本：立即执行爬取 + 微信发送，用于测试新格式。"""
import sys, os, json, logging

os.chdir(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("XINWEN_API_PORT", "5501")
os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:7890")
os.environ.setdefault("HTTPS_PROXY", "http://127.0.0.1:7890")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("test_send_now")

from database import init_db
from sources import register_all

init_db()
register_all()

# ---- 1) 爬取 ----
logger.info("========== 开始爬取 ==========")
from crawl_engine import run_crawl
summary = run_crawl()
logger.info("爬取完成: %s", json.dumps(summary, ensure_ascii=False, indent=2))

# ---- 2) 读取最新 brief 并展示微信文本 ----
from config import PUBLIC_BASE_URL, WECHAT_SEND_TO
from brief_service import load_brief_snapshot
from datetime import date, timedelta

report_date = date.today().strftime("%Y-%m-%d")
data = load_brief_snapshot(report_date)
if not data:
    for i in range(1, 8):
        d = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
        data = load_brief_snapshot(d)
        if data:
            report_date = d
            break

if data:
    text = data.get("wechat_brief", "")
    logger.info("========== 微信消息预览 ==========")
    print("\n" + text + "\n")
    logger.info("========== 开始发送微信 ==========")
    try:
        from shanxiang_wechat import WeChat
        wechat = WeChat()
        wechat.send(WECHAT_SEND_TO, text)
        logger.info("微信发送成功，目标: %s，长度: %d", WECHAT_SEND_TO, len(text))
    except Exception:
        logger.exception("微信发送失败")
else:
    logger.warning("未找到任何 brief 缓存数据")

logger.info("========== 完成 ==========")
