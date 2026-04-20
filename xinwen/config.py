import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "news.db"

EXCEL_PATH = BASE_DIR / "出版、知识产权行业专业数据源汇总.xlsx"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

TEMPLATES_DIR = BASE_DIR / "templates"

PROXY = "http://127.0.0.1:7890"

PROXIES = {
    "http": PROXY,
    "https": PROXY,
}

CRAWL_SCHEDULE_HOUR = 6
CRAWL_SCHEDULE_MINUTE = 30

WECHAT_SEND_HOUR = 7
WECHAT_SEND_MINUTE = 0
WECHAT_BRIEF_API = "https://me6lyl8xtw9bg7x.shanxiangjiaoyu.com/xinwen/api/news/today/brief"
WECHAT_SEND_TO = "文件传输助手"

REQUEST_TIMEOUT = 30
MAX_RETRIES = 3
MIN_DELAY = 1.0
MAX_DELAY = 3.0

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
]

API_HOST = os.environ.get("XINWEN_API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("XINWEN_API_PORT", "8866"))

# 反向代理路径前缀（不剥离前缀时网关会把 /xinwen/api/... 原样转发，需由应用剥掉 /xinwen）
# 例: XINWEN_URL_PREFIX=/xinwen
URL_PREFIX = (os.environ.get("XINWEN_URL_PREFIX") or "").strip().rstrip("/")
if URL_PREFIX and not URL_PREFIX.startswith("/"):
    URL_PREFIX = "/" + URL_PREFIX

# 可选：前端静态资源目录，挂载到 /ui（避免与根路径 JSON 冲突）
FRONTEND_STATIC_DIR = (os.environ.get("XINWEN_FRONTEND_DIR") or "").strip()

# 简报末尾「详细文章请查看」的完整 URL 前缀（不要尾斜杠）
# 例: https://me6lyl8xtw9bg7x.shanxiangjiaoyu.com/xinwen 或 http://本机IP:8866
PUBLIC_BASE_URL = os.environ.get("XINWEN_PUBLIC_BASE_URL", "https://me6lyl8xtw9bg7x.shanxiangjiaoyu.com/xinwen").rstrip("/")

# ---- 可选：大模型生成「关键摘要」（OpenAI 兼容 POST …/v1/chat/completions）----
# 默认走本机 SXAI；无服务时请求失败会自动回退规则摘要。线上请改用环境变量覆盖密钥。
LLM_SUMMARY_ENABLED = os.environ.get("XINWEN_LLM_SUMMARY", "1").lower() in ("1", "true", "yes")
LLM_API_BASE = os.environ.get("XINWEN_LLM_API_BASE", "http://127.0.0.1:8002").rstrip("/")
LLM_API_KEY = os.environ.get(
    "XINWEN_LLM_API_KEY",
    "pk-ydnhw4hb7n5hk6wd1pg7uu0vgyljekzs",
)
LLM_MODEL = os.environ.get("XINWEN_LLM_MODEL", "SXAI-1.0")
LLM_TIMEOUT = int(os.environ.get("XINWEN_LLM_TIMEOUT", "120"))
# 本机模型默认不走系统代理；访问外网 OpenAI 等时设 XINWEN_LLM_USE_PROXY=1
LLM_USE_PROXY = os.environ.get("XINWEN_LLM_USE_PROXY", "0").lower() not in ("0", "false", "no")

# TikHub API 配置（用于获取微信公众号文章）
# 注册地址：https://tikhub.io  -> 用户中心 -> API令牌
TIKHUB_API_TOKEN = os.environ.get(
    "TIKHUB_API_TOKEN",
    "jKkyAsE6/EmNwWyKMaON5jbObBGyaoZtux3/lBWRdbmiqVqXJHPeWyydaA=="
)
TIKHUB_API_BASE = "https://api.tikhub.io"
