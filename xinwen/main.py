from __future__ import annotations
import logging
import sys
from datetime import date, timedelta, datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config import (
    OUTPUT_DIR,
    API_HOST,
    API_PORT,
    URL_PREFIX,
    FRONTEND_STATIC_DIR,
)
from path_prefix_middleware import PrefixStripMiddleware
from brief_service import (
    apply_dynamic_public_url,
    compute_brief_response,
    load_brief_snapshot,
    save_brief_snapshot,
)
from database import init_db, get_articles_by_date, get_crawl_logs
from sources import register_all
from scheduler import start_scheduler, stop_scheduler
from crawl_engine import run_crawl
from html_generator import generate_news_page
from report_generator import generate_report_page

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("xinwen.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    register_all()
    start_scheduler()
    logger.info("Application started")
    yield
    stop_scheduler()
    logger.info("Application stopped")


_fa_kw: dict = {
    "title": "出版与知识产权行业新闻聚合系统",
    "description": "每日自动爬取出版与知识产权行业新闻，生成HTML日报",
    "version": "1.0.0",
    "lifespan": lifespan,
}
if URL_PREFIX:
    _fa_kw["root_path"] = URL_PREFIX

app = FastAPI(**_fa_kw)

if URL_PREFIX:
    app.add_middleware(PrefixStripMiddleware, prefix=URL_PREFIX)
    logger.info("URL prefix strip enabled for gateway path: %s", URL_PREFIX)

app.mount("/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")

_fd = Path(FRONTEND_STATIC_DIR) if FRONTEND_STATIC_DIR else None
if _fd and _fd.is_dir():
    app.mount("/ui", StaticFiles(directory=str(_fd), html=True), name="ui")
    logger.info("Frontend static mounted at /ui from %s", _fd)


def _resolve_today_digest() -> dict[str, Any]:
    """日报文件名为今天，文章 publish_date 为昨天；与 get_latest_news 逻辑一致。"""
    today_str = date.today().strftime("%Y-%m-%d")
    content_date = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    html_file = OUTPUT_DIR / f"news_{today_str}.html"
    report_date = today_str
    if not html_file.exists():
        for i in range(1, 8):
            d = (date.today() - timedelta(days=i)).strftime("%Y-%m-%d")
            f = OUTPUT_DIR / f"news_{d}.html"
            if f.exists():
                report_date = d
                html_file = f
                content_date = (date.today() - timedelta(days=i + 1)).strftime("%Y-%m-%d")
                break

    articles = get_articles_by_date(content_date)
    return {
        "report_date": report_date,
        "content_date": content_date,
        "html_file": html_file,
        "articles": articles,
    }


@app.get("/api/news/today/brief")
def get_today_news_brief():
    """获取当天日报链接与资讯概要。优先返回 6:30 定时任务已落盘的 brief_*.json（7 点 RPA 零等待）。"""
    r = _resolve_today_digest()
    report_date = r["report_date"]
    content_date = r["content_date"]
    html_file: Path = r["html_file"]
    articles: list[dict] = r["articles"]

    cached = load_brief_snapshot(report_date)
    if cached:
        out = apply_dynamic_public_url(cached)
        out["brief_from_cache"] = True
        return out

    out = compute_brief_response(articles, report_date, content_date, html_file)
    out["brief_from_cache"] = False
    return out


@app.get("/api/news/latest")
def get_latest_news():
    """获取最新一期新闻日报（文件名为今天，内容为昨天）"""
    r = _resolve_today_digest()
    report_date = r["report_date"]
    content_date = r["content_date"]
    html_file: Path = r["html_file"]
    articles: list[dict] = r["articles"]
    html_content = ""
    html_url = ""

    if html_file.exists():
        html_content = html_file.read_text(encoding="utf-8")
        html_url = f"/output/news_{report_date}.html"

    sources = set(a["source_name"] for a in articles)

    return {
        "date": report_date,
        "content_date": content_date,
        "html_url": html_url,
        "html_content": html_content,
        "article_count": len(articles),
        "source_count": len(sources),
        "articles": articles,
    }


@app.get("/api/news/{target_date}")
def get_news_by_date(target_date: str):
    """获取指定日期的新闻日报"""
    try:
        datetime.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")

    articles = get_articles_by_date(target_date)

    html_file = OUTPUT_DIR / f"news_{target_date}.html"
    html_content = ""
    html_url = ""

    if html_file.exists():
        html_content = html_file.read_text(encoding="utf-8")
        html_url = f"/output/news_{target_date}.html"

    sources = set(a["source_name"] for a in articles)

    return {
        "date": target_date,
        "html_url": html_url,
        "html_content": html_content,
        "article_count": len(articles),
        "source_count": len(sources),
        "articles": articles,
    }


@app.post("/api/crawl/trigger")
def trigger_crawl(background_tasks: BackgroundTasks, target_date: Optional[str] = None):
    """手动触发爬取任务"""
    if target_date:
        try:
            dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="日期格式错误，请使用 YYYY-MM-DD")
    else:
        dt = date.today() - timedelta(days=1)

    background_tasks.add_task(run_crawl, dt)

    return {
        "status": "started",
        "target_date": dt.strftime("%Y-%m-%d"),
        "message": f"爬取任务已启动，目标日期: {dt.strftime('%Y-%m-%d')}",
    }


@app.get("/api/crawl/status")
def get_crawl_status(crawl_date: Optional[str] = None):
    """查看爬取日志"""
    logs = get_crawl_logs(crawl_date)
    return {
        "crawl_date": crawl_date,
        "logs": logs,
        "total": len(logs),
    }


@app.get("/api/news/{target_date}/html", response_class=HTMLResponse)
def get_news_html(target_date: str):
    """直接返回HTML新闻页面"""
    html_file = OUTPUT_DIR / f"news_{target_date}.html"
    if not html_file.exists():
        articles = get_articles_by_date(target_date)
        if articles:
            generate_news_page(target_date)
        else:
            raise HTTPException(status_code=404, detail=f"未找到 {target_date} 的新闻数据")

    return HTMLResponse(content=html_file.read_text(encoding="utf-8"))


@app.post("/api/news/{target_date}/regenerate")
def regenerate_html(target_date: str):
    """重新生成指定内容日期的 HTML，并刷新对应日报的简报缓存（若文件名可解析）。"""
    articles = get_articles_by_date(target_date)
    if not articles:
        raise HTTPException(status_code=404, detail=f"未找到 {target_date} 的新闻数据")

    path = generate_news_page(target_date)
    if path:
        name = path.name
        if name.startswith("news_") and name.endswith(".html"):
            report_date = name[5:-5]
            save_brief_snapshot(report_date, target_date, articles, path)
    return {
        "status": "success",
        "date": target_date,
        "html_path": str(path),
        "article_count": len(articles),
    }


@app.post("/api/news/{target_date}/regenerate-report")
def regenerate_report(target_date: str):
    """重新生成指定内容日期的叙事式简报 report HTML。"""
    articles = get_articles_by_date(target_date)
    if not articles:
        raise HTTPException(status_code=404, detail=f"未找到 {target_date} 的新闻数据")

    path = generate_report_page(target_date, articles=articles)
    if not path:
        raise HTTPException(status_code=500, detail="简报生成失败（LLM 可能未返回内容）")

    report_date = path.name.replace("report_", "").replace(".html", "")
    html_file = OUTPUT_DIR / f"news_{report_date}.html"
    save_brief_snapshot(report_date, target_date, articles, html_file)

    return {
        "status": "success",
        "date": target_date,
        "report_path": str(path),
        "article_count": len(articles),
    }


@app.get("/api/weixin/accounts")
def get_weixin_accounts():
    """查看微信公众号配置"""
    import json
    config_path = OUTPUT_DIR.parent / "weixin_accounts.json"
    if not config_path.exists():
        return {"accounts": [], "message": "配置文件不存在"}
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    accounts = data.get("accounts", [])
    configured = sum(1 for a in accounts if a.get("ghid"))
    return {
        "total": len(accounts),
        "configured": configured,
        "unconfigured": len(accounts) - configured,
        "accounts": accounts,
    }


@app.post("/api/wechat/send")
def trigger_wechat_send(background_tasks: BackgroundTasks):
    from wechat_sender import send_daily_brief
    background_tasks.add_task(send_daily_brief)
    return {"status": "started", "message": "微信发送任务已触发"}


@app.get("/")
def root():
    return {
        "name": "出版与知识产权行业新闻聚合系统",
        "version": "1.0.0",
        "endpoints": {
            "当天简报URL与概要": "/api/news/today/brief（优先读 6:30 已保存的 output/brief_日期.json）",
            "最新新闻": "/api/news/latest",
            "指定日期新闻": "/api/news/{YYYY-MM-DD}",
            "新闻HTML页面": "/api/news/{YYYY-MM-DD}/html",
            "手动触发爬取": "POST /api/crawl/trigger?target_date=YYYY-MM-DD",
            "爬取状态": "/api/crawl/status",
            "重新生成HTML": "POST /api/news/{YYYY-MM-DD}/regenerate",
            "重新生成叙事简报": "POST /api/news/{YYYY-MM-DD}/regenerate-report",
            "公众号配置": "/api/weixin/accounts",
        },
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)
