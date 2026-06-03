from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class Store(IdMixin, TimestampMixin, Base):
    """加盟店（章节 6）。"""

    __tablename__ = "stores"

    name: Mapped[str] = mapped_column(String(128))
    contact_name: Mapped[str] = mapped_column(String(64))
    contact_phone: Mapped[str] = mapped_column(String(20), index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))

    province: Mapped[Optional[str]] = mapped_column(String(32))
    city: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    district: Mapped[Optional[str]] = mapped_column(String(32))
    address: Mapped[Optional[str]] = mapped_column(String(256))
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 6))
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 6))

    # 管理费比例（千分位）
    management_fee_bps: Mapped[int] = mapped_column(Integer, default=100)  # 默认 10%
    # 结算模式：self（自主结算）/ unified（统一结算）
    settle_mode: Mapped[str] = mapped_column(String(16), default="unified")

    # 收款账户
    bank_card_no: Mapped[Optional[str]] = mapped_column(String(32))
    bank_name: Mapped[Optional[str]] = mapped_column(String(64))
    wechat_pay_id: Mapped[Optional[str]] = mapped_column(String(64))

    # 门店优惠（JSON，例如满减 / 折扣）
    promotions: Mapped[Optional[list]] = mapped_column(JSON)

    # 账户余额（自主结算模式下用）
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)

    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/approved/rejected/disabled
    rejected_reason: Mapped[Optional[str]] = mapped_column(String(256))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")


class StoreStaff(IdMixin, TimestampMixin, Base):
    """店员（章节 4.1.2）。"""

    __tablename__ = "store_staff"

    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(128))
    role: Mapped[str] = mapped_column(String(16), default="staff")  # store_admin/staff
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Device(IdMixin, TimestampMixin, Base):
    """T 恤打印机设备（章节 4.1.2 设备管理）。"""

    __tablename__ = "devices"

    sn: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64))
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), index=True)
    model: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="idle")  # idle/printing/error/offline
    online: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    ink_level: Mapped[int] = mapped_column(Integer, default=100)  # 0~100
    last_heartbeat_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]] = mapped_column(String(256))


class DeviceStatusLog(IdMixin, TimestampMixin, Base):
    __tablename__ = "device_status_logs"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(16))
    to_status: Mapped[str] = mapped_column(String(16))
    ink_level: Mapped[Optional[int]] = mapped_column(Integer)
    message: Mapped[Optional[str]] = mapped_column(String(256))
