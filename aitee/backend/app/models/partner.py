from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class Partner(IdMixin, TimestampMixin, Base):
    """联营伙伴（章节 5）。"""

    __tablename__ = "partners"

    name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))
    channel: Mapped[Optional[str]] = mapped_column(String(64))  # 推广渠道
    id_card: Mapped[Optional[str]] = mapped_column(String(32))
    bank_card_no: Mapped[Optional[str]] = mapped_column(String(32))
    bank_name: Mapped[Optional[str]] = mapped_column(String(64))
    wechat_pay_id: Mapped[Optional[str]] = mapped_column(String(64))

    # 分润比例（0~1，存千分位整数避免浮点：例如 12.5% 存 125）
    ratio_bps: Mapped[int] = mapped_column(default=100)  # 默认 10%

    # 余额（元）
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_payout: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_withdrawn: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/approved/rejected/disabled
    rejected_reason: Mapped[Optional[str]] = mapped_column(String(256))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
