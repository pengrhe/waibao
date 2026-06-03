from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class PayoutRecord(IdMixin, TimestampMixin, Base):
    """分润流水（伙伴）。"""

    __tablename__ = "payout_records"

    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.id"), index=True)
    order_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    ratio: Mapped[float] = mapped_column(Numeric(5, 4))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(16), default="recorded")  # recorded/paid/canceled
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class SettleRecord(IdMixin, TimestampMixin, Base):
    """加盟店结算记录（按月或按单）。"""

    __tablename__ = "settle_records"

    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    mode: Mapped[str] = mapped_column(String(16))  # self/unified
    period_start: Mapped[Optional[date]] = mapped_column(Date)
    period_end: Mapped[Optional[date]] = mapped_column(Date)
    order_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("orders.id"), index=True
    )  # self 模式按单时填
    gross_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    management_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    status: Mapped[str] = mapped_column(String(16), default="recorded")  # recorded/paid
    settled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Withdrawal(IdMixin, TimestampMixin, Base):
    """提现申请（伙伴 + 加盟店共用）。"""

    __tablename__ = "withdrawals"

    owner_type: Mapped[str] = mapped_column(String(16))  # partner/store
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    bank_card: Mapped[Optional[str]] = mapped_column(String(64))
    bank_name: Mapped[Optional[str]] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/approved/paid/rejected
    audit_remark: Mapped[Optional[str]] = mapped_column(String(256))
    audited_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admin_users.id"))
    audited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Reconciliation(IdMixin, TimestampMixin, Base):
    """每日对账（自动 + 手动）。"""

    __tablename__ = "reconciliations"

    date: Mapped[date] = mapped_column(Date, unique=True, index=True)
    source: Mapped[str] = mapped_column(String(16), default="auto")  # auto/manual
    total_revenue: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_payout: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_mgmt_fee: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    expected_net: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    actual_net: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    diff: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    abnormal_count: Mapped[int] = mapped_column(Integer, default=0)
    abnormal_details: Mapped[Optional[list]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(16), default="ok")  # ok/warning/error
    confirmed_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admin_users.id"))
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
