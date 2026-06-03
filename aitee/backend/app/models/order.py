from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import BigIdMixin, IdMixin, TimestampMixin


class Order(BigIdMixin, TimestampMixin, Base):
    __tablename__ = "orders"

    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), index=True)

    # 订单分类（docx 章节 2.2）
    category: Mapped[str] = mapped_column(
        String(16), default="personal"
    )  # personal/enterprise_batch/city_ip/offline

    # 下单渠道
    channel: Mapped[str] = mapped_column(
        String(16), default="h5"
    )  # h5/wx_app/dy_app/offline_store

    # 关联门店/伙伴（章节 4/5）
    store_id: Mapped[Optional[int]] = mapped_column(ForeignKey("stores.id"), index=True)
    partner_id: Mapped[Optional[int]] = mapped_column(ForeignKey("partners.id"), index=True)

    address_id: Mapped[Optional[int]] = mapped_column(ForeignKey("addresses.id"))
    delivery_type: Mapped[str] = mapped_column(String(16), default="pickup")  # pickup/express

    # 金额（单位：元，Numeric 保留 2 位）
    amount_goods: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    amount_shipping: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    amount_discount: Mapped[float] = mapped_column(Numeric(10, 2), default=0)
    amount_total: Mapped[float] = mapped_column(Numeric(10, 2), default=0)

    coupon_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_coupons.id"))

    # 状态流转：pending_pay → paid → pending_print → printing → printed → picked → completed
    # 异常：canceled / refunded
    status: Mapped[str] = mapped_column(String(20), default="pending_pay", index=True)

    pay_method: Mapped[Optional[str]] = mapped_column(String(16))  # wechat/douyin/mock
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    canceled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    remark: Mapped[Optional[str]] = mapped_column(String(512))
    extra: Mapped[Optional[dict]] = mapped_column(JSON)


class OrderItem(BigIdMixin, TimestampMixin, Base):
    __tablename__ = "order_items"

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
    )
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"))
    sku_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_skus.id"))
    design_id: Mapped[Optional[int]] = mapped_column(ForeignKey("designs.id"))

    name_snapshot: Mapped[str] = mapped_column(String(128))
    color_snapshot: Mapped[Optional[str]] = mapped_column(String(32))
    size_snapshot: Mapped[Optional[str]] = mapped_column(String(16))
    preview_url: Mapped[Optional[str]] = mapped_column(String(512))

    unit_price: Mapped[float] = mapped_column(Numeric(10, 2))
    qty: Mapped[int] = mapped_column(Integer, default=1)
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2))


class OrderStatusLog(IdMixin, TimestampMixin, Base):
    __tablename__ = "order_status_logs"

    order_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("orders.id", ondelete="CASCADE"),
        index=True,
    )
    from_status: Mapped[Optional[str]] = mapped_column(String(20))
    to_status: Mapped[str] = mapped_column(String(20))
    operator_type: Mapped[str] = mapped_column(String(16))  # user/staff/admin/system
    operator_id: Mapped[Optional[int]] = mapped_column(Integer)
    reason: Mapped[Optional[str]] = mapped_column(String(256))
