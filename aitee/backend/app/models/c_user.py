from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models._base import BigIdMixin, IdMixin, TimestampMixin


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, index=True)
    openid_wx: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)
    openid_dy: Mapped[Optional[str]] = mapped_column(String(64), unique=True, index=True)
    nickname: Mapped[Optional[str]] = mapped_column(String(64))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512))
    gender: Mapped[Optional[str]] = mapped_column(String(8))
    city: Mapped[Optional[str]] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(16), default="active", server_default="active")
    tags: Mapped[Optional[dict]] = mapped_column(JSON)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Address(IdMixin, TimestampMixin, Base):
    __tablename__ = "addresses"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    receiver: Mapped[str] = mapped_column(String(32))
    phone: Mapped[str] = mapped_column(String(20))
    province: Mapped[str] = mapped_column(String(32))
    city: Mapped[str] = mapped_column(String(32))
    district: Mapped[str] = mapped_column(String(32))
    detail: Mapped[str] = mapped_column(String(256))
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")


class UserPref(IdMixin, TimestampMixin, Base):
    """偏好学习：记录用户多次选择，连续 N 次同值后作为默认值。"""

    __tablename__ = "user_prefs"
    __table_args__ = (UniqueConstraint("user_id", "pref_type", "value", name="uq_user_pref"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    pref_type: Mapped[str] = mapped_column(String(32))
    value: Mapped[str] = mapped_column(String(128))
    count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class Design(BigIdMixin, TimestampMixin, Base):
    """设计稿：编辑器图层 JSON + 预览图。"""

    __tablename__ = "designs"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(128), default="未命名设计")
    product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id", ondelete="SET NULL"))
    sku_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_skus.id", ondelete="SET NULL"))
    side: Mapped[str] = mapped_column(String(8), default="front")
    layers: Mapped[Optional[list]] = mapped_column(JSON)
    preview_url: Mapped[Optional[str]] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(String(16), default="draft")


class CartItem(BigIdMixin, TimestampMixin, Base):
    __tablename__ = "cart_items"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    design_id: Mapped[Optional[int]] = mapped_column(ForeignKey("designs.id", ondelete="SET NULL"))
    sku_id: Mapped[int] = mapped_column(ForeignKey("product_skus.id", ondelete="RESTRICT"))
    qty: Mapped[int] = mapped_column(Integer, default=1)
    selected: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    snapshot: Mapped[Optional[dict]] = mapped_column(JSON)
