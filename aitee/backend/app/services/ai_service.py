"""AI 出图服务：优先调 active 模型通道；失败/无 key 时 fallback 到 placeholder。

设计：
- model_channels 表里 is_active=True 的通道作为当前激活模型。
- 当前 OpenRouter google/gemini-3-pro 主要是文本/多模态推理模型，图片生成接入路径取决于 OR 后续支持。
  这里实现一个 "尝试 + fallback" 的策略，保证 demo 永远有图可显，不阻塞前后端联调。
"""
from __future__ import annotations

import asyncio
import base64
import hashlib
import logging
import time
from pathlib import Path
from typing import List, Optional, Tuple

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import AiGeneration, ModelChannel

logger = logging.getLogger("aitee.ai")


# ============== 占位图 fallback ==============

PLACEHOLDER_SEEDS = [
    "aitee-art1", "aitee-art2", "aitee-art3", "aitee-art4",
    "aitee-art5", "aitee-art6", "aitee-art7", "aitee-art8",
    "aitee-art9", "aitee-art10", "aitee-art11", "aitee-art12",
]


def placeholder_images(n: int, prompt: str = "", style: str = "") -> List[str]:
    """生成稳定的占位图链接（按 prompt 哈希选 seed，保证同 prompt 同图）。"""
    base_seed = hashlib.md5(f"{prompt}|{style}".encode("utf-8")).hexdigest()[:6]
    urls = []
    for i in range(n):
        seed = f"{base_seed}-{i}"
        urls.append(f"https://picsum.photos/seed/{seed}/512/512")
    return urls


# ============== 模型通道选择 ==============

def get_active_channel(db: Session) -> Optional[ModelChannel]:
    return db.execute(
        select(ModelChannel).where(ModelChannel.is_active == True, ModelChannel.enabled == True)  # noqa: E712
    ).scalar_one_or_none()


# ============== 调真实模型（按 provider 分流）==============

async def _call_openrouter_image(
    channel: ModelChannel,
    *,
    prompt: str,
    n: int,
    style: Optional[str],
    source_image_url: Optional[str],
) -> Optional[List[str]]:
    """尝试调 OpenRouter 出图。

    注意：OpenRouter 出图能力目前仅支持部分模型（如 black-forest-labs/flux-1.1-pro 等）。
    gemini-3-pro 主要是文本/多模态理解，无图像生成接口。此函数若返回 None 表示该通道不支持出图。
    """
    model_lower = channel.model_name.lower()
    supports_image = any(k in model_lower for k in ["flux", "imagen", "dall-e", "sdxl", "stable-diffusion", "image"])
    if not supports_image:
        logger.info(f"channel {channel.name} ({channel.model_name}) 不支持出图，跳过")
        return None

    url = f"{channel.base_url.rstrip('/')}/images/generations"
    payload = {
        "model": channel.model_name,
        "prompt": f"{prompt}{(' style:'+style) if style else ''}",
        "n": n,
        "size": "1024x1024",
    }
    headers = {
        "Authorization": f"Bearer {channel.api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            logger.warning(f"openrouter image error {r.status_code}: {r.text[:200]}")
            return None
        data = r.json()
        urls = []
        for item in data.get("data", []):
            if item.get("url"):
                urls.append(item["url"])
            elif item.get("b64_json"):
                urls.append(f"data:image/png;base64,{item['b64_json']}")
        return urls or None
    except Exception as e:
        logger.exception(f"openrouter image call failed: {e}")
        return None


async def _call_openrouter_chat_describe(
    channel: ModelChannel,
    *,
    prompt: str,
) -> Optional[str]:
    """用 chat completion 接口让模型生成一段描述（demo 用：证明通道可调通）。"""
    url = f"{channel.base_url.rstrip('/')}/chat/completions"
    payload = {
        "model": channel.model_name,
        "messages": [
            {"role": "system", "content": "你是 aitee 文化 IP 设计师，用 1 句话扩写用户的设计概念，不超过 40 字。"},
            {"role": "user", "content": prompt or "深圳科技感 T 恤图案"},
        ],
        "max_tokens": 120,
    }
    headers = {
        "Authorization": f"Bearer {channel.api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            return None
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception:
        return None


# ============== 对外 API ==============

async def generate(
    db: Session,
    *,
    user_id: Optional[int],
    type_: str = "t2i",
    prompt: Optional[str] = None,
    style: Optional[str] = None,
    source_image_url: Optional[str] = None,
    n: int = 4,
) -> Tuple[List[dict], bool, str]:
    """统一出图入口。返回 (samples, fallback, status)。

    samples: [{id, image_url, thumb_url, prompt, style}]
    fallback: True 表示走了占位图
    """
    start = time.time()
    n = max(1, min(n, 8))
    prompt = (prompt or "潮流原创 T 恤图案").strip()

    channel = get_active_channel(db)
    fallback = False
    image_urls: List[str] = []

    if channel:
        urls = await _call_openrouter_image(channel, prompt=prompt, n=n, style=style, source_image_url=source_image_url)
        if urls:
            image_urls = urls
        else:
            # 顺手调一下 chat 验证下通道可达性（不阻塞）
            try:
                await asyncio.wait_for(_call_openrouter_chat_describe(channel, prompt=prompt), timeout=10)
            except Exception:
                pass

    if not image_urls:
        image_urls = placeholder_images(n, prompt=prompt, style=style or "")
        fallback = True

    samples = []
    for i, url in enumerate(image_urls):
        samples.append({
            "id": int(time.time() * 1000) + i,
            "image_url": url,
            "thumb_url": url,
            "prompt": prompt,
            "style": style,
        })

    # 写历史
    gen = AiGeneration(
        user_id=user_id,
        type=type_,
        prompt=prompt,
        style=style,
        source_image_url=source_image_url,
        model_channel_id=channel.id if channel else None,
        n=n,
        status="fallback" if fallback else "success",
        result_urls=[s["image_url"] for s in samples],
        duration_ms=int((time.time() - start) * 1000),
    )
    db.add(gen)
    db.commit()

    return samples, fallback, "fallback" if fallback else "success"
