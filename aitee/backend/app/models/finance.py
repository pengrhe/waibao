"""B 端财务域：分润流水 / 加盟店结算 / 提现 / 对账。"""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class PayoutRecord(IdMixin, TimestampMixin, Base):
    """分润流水：每个伙伴下单订单产生一条。"""

    __tablename__ = "payout_records"

    order_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    partner_id: Mapped[int] = mapped_column(ForeignKey("partners.id"), index=True)
    order_amount: Mapped[float] = mapped_column(Numeric(10, 2))
    ratio_bps: Mapped[int] = mapped_column(Integer)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(16), default="recorded")  # recorded/paid/reversed
    booked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    remark: Mapped[Optional[str]] = mapped_column(String(256))


class SettleRecord(IdMixin, TimestampMixin, Base):
    """加盟店结算（按月）。"""

    __tablename__ = "settle_records"

    store_id: Mapped[int] = mapped_column(ForeignKey("stores.id"), index=True)
    period_start: Mapped[date] = mapped_column(Date)
    period_end: Mapped[date] = mapped_column(Date)
    mode: Mapped[str] = mapped_column(String(16))  # self/unified
    total_revenue: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    management_fee: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    net_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0)
    order_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="pending")  # pending/paid/reversed
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    detail: Mapped[Optional[dict]] = mapped_column(JSON)


class Withdrawal(IdMixin, TimestampMixin, Base):
    """提现申请（伙伴/加盟店都用）。"""

    __tablename__ = "withdrawals"

    owner_type: Mapped[str] = mapped_column(String(16))  # partner/store
    owner_id: Mapped[int] = mapped_column(Integer, index=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2))
    bank_card_no: Mapped[Optional[str]] = mapped_column(String(32))
    bank_name: Mapped[Optional[str]] = mapped_column(String(64))
    wechat_pay_id: Mapped[Optional[str]] = mapped_column(String(64))
    method: Mapped[str] = mapped_column(String(16), default="bank")  # bank/wechat
    status: Mapped[str] = mapped_column(String(16), default="pending")
    # pending/approved/paid/rejected
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    audited_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    auditor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("admin_users.id"))
    rejected_reason: Mapped[Optional[str]] = mapped_column(String(256))


class Reconciliation(IdMixin, TimestampMixin, Base):
    """对账（每日凌晨自动 + 支持手动核对）。"""

    __tablename__ = "reconciliations"

    day: Mapped[date] = mapped_column(Date, unique=True, index=True)
    source: Mapped[str] = mapped_column(String(8), default="auto")  # auto/manual
    total_revenue: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_payout: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    total_management_fee: Mapped[float] = mapped_column(Numeric(14, 2), default=0)
    abnormal_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="ok")  # ok/abnormal/resolved
    detail: Mapped[Optional[dict]] = mapped_column(JSON)
    resolved_by: Mapped[Optional[int]] = mapped_column(ForeignKey("admin_users.id"))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
