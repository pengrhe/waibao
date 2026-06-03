from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class QrCode(IdMixin, TimestampMixin, Base):
    """统一二维码表：伙伴分润码 / 门店下单码 / 店员核销码 / 订单核销码。"""

    __tablename__ = "qr_codes"
    __table_args__ = (
        UniqueConstraint("type", "owner_id", "scene", name="uq_qr_owner_scene"),
    )

    type: Mapped[str] = mapped_column(String(24), index=True)
    # partner_split / store_order / staff_verify / order_verify
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    scene: Mapped[str] = mapped_column(String(32), default="default")

    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    style: Mapped[Optional[dict]] = mapped_column(JSON)  # 自定义 logo/背景等

    scan_count: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
