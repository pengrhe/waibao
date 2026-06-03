from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class Coupon(IdMixin, TimestampMixin, Base):
    """优惠券模板。"""

    __tablename__ = "coupons"

    name: Mapped[str] = mapped_column(String(64))
    type: Mapped[str] = mapped_column(String(16))  # discount | cash
    value: Mapped[float] = mapped_column(Numeric(10, 2))
    threshold: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    valid_days: Mapped[int] = mapped_column(Integer, default=30)
    total: Mapped[int] = mapped_column(Integer, default=0)
    claimed: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="active")
    description: Mapped[Optional[str]] = mapped_column(String(256))


class UserCoupon(IdMixin, TimestampMixin, Base):
    __tablename__ = "user_coupons"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    coupon_id: Mapped[int] = mapped_column(ForeignKey("coupons.id", ondelete="RESTRICT"), index=True)
    status: Mapped[str] = mapped_column(String(16), default="unused")  # unused/used/expired
    claimed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    expire_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"))

    coupon: Mapped["Coupon"] = relationship("Coupon", lazy="joined")
