from __future__ import annotations
import asyncio
import logging
import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

import edge_tts

from config import PROXY

os.environ.setdefault("HTTP_PROXY", PROXY)
os.environ.setdefault("HTTPS_PROXY", PROXY)

logger = logging.getLogger(__name__)

VOICE = "zh-CN-YunyangNeural"
TRAILING_GAP = 0.5

CN_NUMS = [
    "零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
]


async def _gen_segment(text: str) -> Tuple[bytes, float]:
    """Generate audio bytes and estimated duration (seconds) for one text segment."""
    comm = edge_tts.Communicate(text, VOICE)
    audio = bytearray()
    last_end_ticks = 0

    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
        elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            end = chunk["offset"] + chunk["duration"]
            if end > last_end_ticks:
                last_end_ticks = end

    duration = last_end_ticks / 10_000_000.0 + TRAILING_GAP
    return bytes(audio), duration


async def _generate_all(
    date_str: str,
    categories: Dict[str, List[Dict[str, Any]]],
    total_count: int,
    output_path: Path,
) -> List[Dict[str, Any]]:
    """Build text segments, generate audio, concatenate, and return timeline."""
    segments: List[Dict[str, Any]] = []

    segments.append({
        "text": f"出版与知识产权行业日报，{date_str}，共{total_count}条资讯。",
        "type": "intro",
        "article_idx": -1,
    })

    article_idx = 0
    part_num = 0
    for cat_name, cat_articles in categories.items():
        part_num += 1
        num_str = CN_NUMS[part_num] if part_num < len(CN_NUMS) else str(part_num)
        segments.append({
            "text": f"第{num_str}部分，{cat_name}，共{len(cat_articles)}篇。",
            "type": "cat",
            "article_idx": article_idx,
            "cat_name": cat_name,
        })

        for article in cat_articles:
            title = article.get("title", "")
            summary = (article.get("summary", "") or "").strip()
            source = article.get("source_name", "")

            parts = []
            if source:
                parts.append(source)
            parts.append(title)
            if summary and len(summary) > 10:
                parts.append(summary)

            segments.append({
                "text": "，".join(parts) + "。",
                "type": "article",
                "article_idx": article_idx,
            })
            article_idx += 1

    segments.append({
        "text": "以上就是今日全部资讯，感谢收听。",
        "type": "outro",
        "article_idx": -1,
    })

    all_audio = bytearray()
    timeline: List[Dict[str, Any]] = []
    cumulative = 0.0

    for i, seg in enumerate(segments):
        logger.info("TTS [%d/%d] %s", i + 1, len(segments), seg["text"][:40])
        try:
            audio_bytes, duration = await _gen_segment(seg["text"])
        except Exception:
            logger.exception("TTS segment failed, skipping: %s", seg["text"][:40])
            continue

        entry: Dict[str, Any] = {
            "type": seg["type"],
            "start": round(cumulative, 2),
        }
        if seg["type"] in ("article", "cat") and seg["article_idx"] >= 0:
            entry["idx"] = seg["article_idx"]

        timeline.append(entry)
        all_audio += audio_bytes
        cumulative += duration

    output_path.write_bytes(bytes(all_audio))
    logger.info("TTS saved: %s (%d bytes, ~%.0fs)", output_path, len(all_audio), cumulative)
    return timeline


def generate_tts(
    date_str: str,
    categories: Dict[str, List[Dict[str, Any]]],
    total_count: int,
    output_path: Path,
) -> List[Dict[str, Any]]:
    """Sync entry point — safe to call from threads (FastAPI, APScheduler)."""
    return asyncio.run(
        _generate_all(date_str, categories, total_count, output_path)
    )


import re as _re


def _strip_markdown(text: str) -> str:
    text = _re.sub(r"^#{1,6}\s*", "", text, flags=_re.MULTILINE)
    text = _re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = _re.sub(r"\*(.+?)\*", r"\1", text)
    text = _re.sub(r"^\s*[-*]\s+", "", text, flags=_re.MULTILINE)
    text = _re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.strip()


def _split_report_segments(date_str: str, md_text: str) -> List[Dict[str, Any]]:
    segments: List[Dict[str, Any]] = []
    segments.append({"text": f"知识产权和出版行业简报，{date_str}。", "type": "intro"})

    sections = _re.split(r"(?=^##\s)", md_text, flags=_re.MULTILINE)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = _re.match(r"^##\s*(.+)", section)
        if not heading_match:
            continue
        heading = heading_match.group(1).strip()
        body = _strip_markdown(section[heading_match.end():].strip())
        if not body or body == "本期暂无相关资讯。":
            continue
        for idx, para in enumerate(_re.split(r"\n{2,}", body)):
            para = para.strip()
            if not para:
                continue
            txt = f"{heading}。{para}" if idx == 0 else para
            if len(txt) > 300:
                txt = txt[:300] + "。"
            segments.append({"text": txt, "type": "section"})

    segments.append({"text": "以上就是本期简报全部内容，感谢收听。", "type": "outro"})
    return segments


async def _generate_report_audio(date_str: str, md_text: str, output_path: Path) -> None:
    segments = _split_report_segments(date_str, md_text)
    all_audio = bytearray()
    for i, seg in enumerate(segments):
        logger.info("Report TTS [%d/%d] %s", i + 1, len(segments), seg["text"][:40])
        try:
            audio_bytes, _ = await _gen_segment(seg["text"])
            all_audio += audio_bytes
        except Exception:
            logger.exception("Report TTS segment failed: %s", seg["text"][:40])
    output_path.write_bytes(bytes(all_audio))
    logger.info("Report TTS saved: %s (%d bytes)", output_path, len(all_audio))


def generate_report_tts(date_str: str, md_text: str, output_path: Path) -> bool:
    """Generate TTS audio for narrative report markdown. Returns True on success."""
    try:
        asyncio.run(_generate_report_audio(date_str, md_text, output_path))
        return True
    except Exception:
        logger.exception("Report TTS generation failed")
        return False
