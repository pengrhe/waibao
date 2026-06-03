from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class AdminUser(IdMixin, TimestampMixin, Base):
    """总部账号（B 端 admin）。"""

    __tablename__ = "admin_users"

    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    name: Mapped[Optional[str]] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16), default="admin")  # admin/finance/ops/viewer
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Partner(IdMixin, TimestampMixin, Base):
    """联营伙伴。"""

    __tablename__ = "partners"

    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[Optional[str]] = mapped_column(String(20), index=True)
    channel: Mapped[Optional[str]] = mapped_column(String(64))  # 推广渠道
    profit_ratio: Mapped[float] = mapped_column(Numeric(5, 4), default=0.05)  # 默认 5%
    bank_card: Mapped[Optional[str]] = mapped_column(String(64))
    bank_name: Mapped[Optional[str]] = mapped_column(String(64))
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_earned: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    total_withdrew: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/active/disabled/rejected
    reject_reason: Mapped[Optional[str]] = mapped_column(String(256))
    audited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Store(IdMixin, TimestampMixin, Base):
    """加盟店。"""

    __tablename__ = "stores"

    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    name: Mapped[str] = mapped_column(String(128))
    owner: Mapped[Optional[str]] = mapped_column(String(64))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    province: Mapped[Optional[str]] = mapped_column(String(32))
    city: Mapped[Optional[str]] = mapped_column(String(32), index=True)
    district: Mapped[Optional[str]] = mapped_column(String(32))
    address: Mapped[Optional[str]] = mapped_column(String(256))
    management_fee_ratio: Mapped[float] = mapped_column(Numeric(5, 4), default=0.1)  # 管理费 10%
    settle_mode: Mapped[str] = mapped_column(String(16), default="unified")  # self/unified
    bank_card: Mapped[Optional[str]] = mapped_column(String(64))
    bank_name: Mapped[Optional[str]] = mapped_column(String(64))
    balance: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    promotion: Mapped[Optional[dict]] = mapped_column(JSON)  # 门店优惠：满减/折扣等
    status: Mapped[str] = mapped_column(String(16), default="pending")
    reject_reason: Mapped[Optional[str]] = mapped_column(String(256))
    audited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class StoreStaff(IdMixin, TimestampMixin, Base):
    """店员。"""

    __tablename__ = "store_staff"

    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), index=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    name: Mapped[str] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16), default="staff")  # staff/store_admin
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Device(IdMixin, TimestampMixin, Base):
    """T 恤打印机（mock）。"""

    __tablename__ = "devices"

    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id", ondelete="CASCADE"), index=True)
    sn: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(64))
    model: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="idle")  # idle/printing/error/offline
    ink_level: Mapped[int] = mapped_column(Integer, default=100)  # 0-100
    online: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    last_heartbeat_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    current_order_id: Mapped[Optional[int]] = mapped_column(ForeignKey("orders.id"))


class DeviceStatusLog(IdMixin, TimestampMixin, Base):
    __tablename__ = "device_status_logs"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    from_status: Mapped[Optional[str]] = mapped_column(String(16))
    to_status: Mapped[str] = mapped_column(String(16))
    ink_level: Mapped[Optional[int]] = mapped_column(Integer)
    message: Mapped[Optional[str]] = mapped_column(String(256))
