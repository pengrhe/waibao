from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class QrCode(IdMixin, TimestampMixin, Base):
    """统一二维码：partner_split / store_order / staff_verify / city_share。"""

    __tablename__ = "qr_codes"

    type: Mapped[str] = mapped_column(String(32), index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    owner_type: Mapped[Optional[str]] = mapped_column(String(16))  # partner/store/staff
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    target_url: Mapped[str] = mapped_column(String(512))
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    style: Mapped[Optional[dict]] = mapped_column(JSON)  # logo / 背景色 / 模板
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    scan_count: Mapped[int] = mapped_column(Integer, default=0)


class PushMessage(IdMixin, TimestampMixin, Base):
    """消息推送记录。"""

    __tablename__ = "push_messages"

    user_type: Mapped[str] = mapped_column(String(16))  # c_user/admin/partner/store/staff
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    channel: Mapped[str] = mapped_column(String(16))  # wechat_notify/douyin/inapp/sms
    template: Mapped[Optional[str]] = mapped_column(String(64))
    title: Mapped[str] = mapped_column(String(128))
    body: Mapped[Optional[str]] = mapped_column(String(512))
    link_to: Mapped[Optional[str]] = mapped_column(String(256))
    payload: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/sent/read/failed
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class SystemConfig(IdMixin, TimestampMixin, Base):
    """系统配置 KV：打印价格 / 默认分润比例 / 结算周期 / 渠道开关 / AI 模板 ...。"""

    __tablename__ = "system_configs"

    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    value: Mapped[Optional[dict]] = mapped_column(JSON)
    description: Mapped[Optional[str]] = mapped_column(String(256))
    category: Mapped[str] = mapped_column(String(32), default="general")  # pricing/profit/channel/ai
