"""可选：调用 OpenAI 兼容接口，为微信群简报生成「关键摘要」正文。"""
from __future__ import annotations
import json
import logging
import re
from pathlib import Path
from typing import Any

import requests

from config import (
    LLM_API_BASE,
    LLM_API_KEY,
    LLM_MODEL,
    LLM_SUMMARY_ENABLED,
    LLM_TIMEOUT,
    LLM_USE_PROXY,
    PROXIES,
)

logger = logging.getLogger(__name__)


def _chat_completions_url() -> str:
    """支持 API 根为 http://host:port 或 http://host:port/v1。"""
    base = LLM_API_BASE.rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def _llm_proxies() -> dict | None:
    if not LLM_USE_PROXY:
        return None
    low = LLM_API_BASE.lower()
    if "127.0.0.1" in low or "localhost" in low:
        return None
    return PROXIES


def _html_to_plain_snippet(html_path: Path, max_chars: int = 8000) -> str:
    try:
        from bs4 import BeautifulSoup

        raw = html_path.read_text(encoding="utf-8")
        soup = BeautifulSoup(raw, "lxml")
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        blob = "\n".join(lines)
        return blob[:max_chars]
    except Exception:
        logger.debug("HTML to text snippet failed", exc_info=True)
        return ""


def _build_user_payload(
    articles: list[dict],
    report_date: str,
    html_path: Path | None,
) -> str:
    blocks: list[str] = [f"日报日期（页面标题）: {report_date}", "", "【结构化条目】"]
    for i, a in enumerate(articles, 1):
        cat = a.get("source_category") or ""
        src = a.get("source_name") or ""
        title = (a.get("title") or "").strip()
        summ = (a.get("summary") or "").strip()
        blocks.append(f"{i}. [{cat}] {src}")
        blocks.append(f"   标题: {title}")
        if summ:
            blocks.append(f"   摘要: {summ[:400]}{'…' if len(summ) > 400 else ''}")
        blocks.append("")
    if html_path and html_path.exists():
        snippet = _html_to_plain_snippet(html_path)
        if snippet:
            blocks.append("【当日 HTML 页面正文节选（供交叉参考）】")
            blocks.append(snippet)
    return "\n".join(blocks)


def try_llm_key_summary_body(
    articles: list[dict],
    report_date: str,
    html_path: Path | None = None,
) -> tuple[str | None, str]:
    """
    返回 (摘要正文, 来源标记)。
    摘要正文不含「关键摘要:」前缀；失败或关闭时正文为 None，来源为 disabled / error / empty。
    """
    if not LLM_SUMMARY_ENABLED:
        return None, "disabled"
    if not LLM_API_KEY:
        logger.info("LLM summary enabled but XINWEN_LLM_API_KEY empty, skip")
        return None, "disabled"
    if not articles:
        return None, "empty"

    url = _chat_completions_url()
    user_content = _build_user_payload(articles, report_date, html_path)

    system = (
        "你是出版与知识产权行业资深编辑。根据用户提供的当日资讯素材（结构化条目 + 可选网页正文节选），"
        "写一段 100～200 字的中文「关键摘要」：提炼热点主题、政策或市场信号，可点到具体数据或案例，"
        "不要逐条复述条目；语气专业客观；不要使用 Markdown、不要分点编号、不要「综上所述」等套话，"
        "纯一段话。不要输出标题前缀（不要写「关键摘要：」）。"
    )

    payload: dict[str, Any] = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 512,
        "temperature": 0.4,
    }

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    proxies = _llm_proxies()

    try:
        resp = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=LLM_TIMEOUT,
            proxies=proxies,
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            logger.warning("LLM response has no choices")
            return None, "error"
        content = (choices[0].get("message") or {}).get("content") or ""
        content = content.strip()
        content = re.sub(r"^关键摘要[:：]\s*", "", content)
        content = re.sub(r"\s+", " ", content).strip()
        if len(content) < 20:
            logger.warning("LLM summary too short, fallback")
            return None, "error"
        return content, "llm"
    except Exception:
        logger.exception("LLM key summary failed")
        return None, "error"


_REPORT_SECTIONS = [
    "知识产权领域大事要事",
    "出版行业最新政策",
    "行业数据",
    "市场动态",
    "行业热点",
    "热门新书",
]

_REPORT_SYSTEM_PROMPT = (
    "你是出版与知识产权行业资深编辑。根据用户提供的当日资讯素材，"
    "撰写一份结构化的「知识产权和出版行业简报」。\n\n"
    "要求：\n"
    "1. 报告必须严格按以下六个章节输出，每个章节用 ## 加中文序号作为标题：\n"
    "   ## 一、知识产权领域大事要事\n"
    "   ## 二、出版行业最新政策\n"
    "   ## 三、行业数据\n"
    "   ## 四、市场动态\n"
    "   ## 五、行业热点\n"
    "   ## 六、热门新书\n"
    "2. 每个章节写 2~4 段叙述性内容，综合多条素材进行分析归纳，不要逐条复述。\n"
    "3. 如某个章节确实无对应素材，写一句「本期暂无相关资讯」即可。\n"
    "4. 在引用具体消息来源时，用 **加粗** 标出关键数据和机构名称。\n"
    "5. 「热门新书」章节如有相关素材，用 Markdown 无序列表格式列出书目。\n"
    "6. 语气专业客观，不要使用「综上所述」等套话。\n"
    "7. 不要输出报告标题（标题由系统添加），直接从第一个 ## 章节开始。\n"
    "8. 只输出 Markdown 正文，不要输出其他内容。"
)


def try_llm_full_report(
    articles: list[dict],
    report_date: str,
    html_path: Path | None = None,
) -> str | None:
    """调用 LLM 生成完整的分章节叙事式简报（Markdown）。失败返回 None。"""
    if not LLM_SUMMARY_ENABLED or not LLM_API_KEY or not articles:
        return None

    url = _chat_completions_url()
    user_content = _build_user_payload(articles, report_date, html_path)

    payload: dict[str, Any] = {
        "model": LLM_MODEL,
        "messages": [
            {"role": "system", "content": _REPORT_SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": 4096,
        "temperature": 0.5,
    }

    headers = {
        "Authorization": f"Bearer {LLM_API_KEY}",
        "Content-Type": "application/json",
    }

    proxies = _llm_proxies()

    try:
        resp = requests.post(
            url,
            headers=headers,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            timeout=LLM_TIMEOUT * 2,
            proxies=proxies,
        )
        resp.raise_for_status()
        data = resp.json()
        choices = data.get("choices") or []
        if not choices:
            logger.warning("LLM full report: no choices")
            return None
        content = (choices[0].get("message") or {}).get("content") or ""
        content = content.strip()
        if len(content) < 100:
            logger.warning("LLM full report too short (%d chars)", len(content))
            return None
        logger.info("LLM full report generated: %d chars", len(content))
        return content
    except Exception:
        logger.exception("LLM full report generation failed")
        return None
