from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class ModelChannel(IdMixin, TimestampMixin, Base):
    """AI 模型通道（后台可配置）。"""

    __tablename__ = "model_channels"

    name: Mapped[str] = mapped_column(String(64), unique=True)
    provider: Mapped[str] = mapped_column(String(32))  # openrouter/openai/anthropic/stub
    base_url: Mapped[str] = mapped_column(String(256))
    api_key: Mapped[str] = mapped_column(String(256))  # 后续可加密
    model_name: Mapped[str] = mapped_column(String(128))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1", index=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", index=True
    )  # 同一时刻仅一个 is_active=True
    extra: Mapped[Optional[dict]] = mapped_column(JSON)
    remark: Mapped[Optional[str]] = mapped_column(String(256))


class AiGeneration(IdMixin, TimestampMixin, Base):
    """AI 出图历史。"""

    __tablename__ = "ai_generations"

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(16))  # t2i/i2i/ti2i/city_ip
    prompt: Mapped[Optional[str]] = mapped_column(String(1024))
    style: Mapped[Optional[str]] = mapped_column(String(32))
    source_image_url: Mapped[Optional[str]] = mapped_column(String(512))
    model_channel_id: Mapped[Optional[int]] = mapped_column(ForeignKey("model_channels.id"))
    n: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(16), default="success")  # pending/success/failed/fallback
    result_urls: Mapped[Optional[list]] = mapped_column(JSON)
    error: Mapped[Optional[str]] = mapped_column(String(512))
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    extra: Mapped[Optional[dict]] = mapped_column(JSON)


class AiPreprocessLog(IdMixin, TimestampMixin, Base):
    """AI 预处理记录（清晰化 / 去水印 / 裁边 / 色彩校准）。"""

    __tablename__ = "ai_preprocess_logs"

    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)
    source_file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id"))
    output_file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id"))
    operations: Mapped[Optional[list]] = mapped_column(JSON)  # ["sharpen","dewatermark","crop","colorize"]
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(16), default="success")
    error: Mapped[Optional[str]] = mapped_column(String(512))
