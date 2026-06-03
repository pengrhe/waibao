"""商品 / 印花 / 内容 / 文化元素 等目录类模型。"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class ProductCategory(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_categories"

    name: Mapped[str] = mapped_column(String(32))
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Product(IdMixin, TimestampMixin, Base):
    __tablename__ = "products"

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    subtitle: Mapped[Optional[str]] = mapped_column(String(256))
    base_price: Mapped[float] = mapped_column(Numeric(10, 2))
    main_image_url: Mapped[Optional[str]] = mapped_column(String(512))
    gallery: Mapped[Optional[list]] = mapped_column(JSON)
    description: Mapped[Optional[str]] = mapped_column(String(1024))
    available_colors: Mapped[Optional[list]] = mapped_column(JSON)
    available_sizes: Mapped[Optional[list]] = mapped_column(JSON)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class ProductSku(IdMixin, TimestampMixin, Base):
    __tablename__ = "product_skus"

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), index=True)
    color: Mapped[str] = mapped_column(String(32))
    size: Mapped[str] = mapped_column(String(16))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(Integer, default=999)
    image_url: Mapped[Optional[str]] = mapped_column(String(512))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")


class PatternCategory(IdMixin, TimestampMixin, Base):
    __tablename__ = "pattern_categories"

    name: Mapped[str] = mapped_column(String(32))
    slug: Mapped[str] = mapped_column(String(32), unique=True)
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Pattern(IdMixin, TimestampMixin, Base):
    __tablename__ = "patterns"

    category_id: Mapped[Optional[int]] = mapped_column(ForeignKey("pattern_categories.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    image_url: Mapped[str] = mapped_column(String(512))
    thumb_url: Mapped[Optional[str]] = mapped_column(String(512))
    tags: Mapped[Optional[list]] = mapped_column(JSON)
    source: Mapped[str] = mapped_column(String(16), default="builtin")  # builtin/ai/user
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class Topic(IdMixin, TimestampMixin, Base):
    """首页横滑专区。"""

    __tablename__ = "topics"

    title: Mapped[str] = mapped_column(String(128))
    subtitle: Mapped[Optional[str]] = mapped_column(String(256))
    cover_url: Mapped[Optional[str]] = mapped_column(String(512))
    link_to: Mapped[Optional[str]] = mapped_column(String(256))
    items: Mapped[Optional[list]] = mapped_column(JSON)
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")


class Banner(IdMixin, TimestampMixin, Base):
    __tablename__ = "banners"

    position: Mapped[str] = mapped_column(String(32), index=True)  # home_top / home_mid ...
    title: Mapped[Optional[str]] = mapped_column(String(128))
    image_url: Mapped[str] = mapped_column(String(512))
    link_to: Mapped[Optional[str]] = mapped_column(String(256))
    sort: Mapped[int] = mapped_column(Integer, default=0)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    start_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class FileRecord(IdMixin, TimestampMixin, Base):
    """统一文件登记表（上传 / AI 产物 / 设计预览）。"""

    __tablename__ = "files"

    owner_type: Mapped[str] = mapped_column(String(16))  # user/admin/system
    owner_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    purpose: Mapped[str] = mapped_column(String(16))  # avatar/pattern/design/ai/source/excel
    mime: Mapped[Optional[str]] = mapped_column(String(64))
    size: Mapped[int] = mapped_column(Integer, default=0)
    url: Mapped[str] = mapped_column(String(512))
    width: Mapped[Optional[int]] = mapped_column(Integer)
    height: Mapped[Optional[int]] = mapped_column(Integer)
    extra: Mapped[Optional[dict]] = mapped_column(JSON)


class CulturalElement(IdMixin, TimestampMixin, Base):
    """城市文化元素库（后台可维护，AI 城市 IP 生成时引用）。"""

    __tablename__ = "cultural_elements"

    city: Mapped[str] = mapped_column(String(64), index=True)
    name: Mapped[str] = mapped_column(String(64))
    category: Mapped[str] = mapped_column(String(16))  # landmark/folk/symbol/food/dialect
    description: Mapped[Optional[str]] = mapped_column(String(256))
    style_hint: Mapped[Optional[str]] = mapped_column(String(64))
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class CityIp(IdMixin, TimestampMixin, Base):
    __tablename__ = "city_ips"

    city: Mapped[str] = mapped_column(String(64), unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(256))
    cover_url: Mapped[Optional[str]] = mapped_column(String(512))


class CityIpItem(IdMixin, TimestampMixin, Base):
    __tablename__ = "city_ip_items"

    city_ip_id: Mapped[int] = mapped_column(ForeignKey("city_ips.id", ondelete="CASCADE"), index=True)
    category: Mapped[str] = mapped_column(String(16))  # landmark/folk/symbol
    title: Mapped[str] = mapped_column(String(128))
    image_url: Mapped[str] = mapped_column(String(512))
    source: Mapped[str] = mapped_column(String(16), default="builtin")
    sort: Mapped[int] = mapped_column(Integer, default=0)


class CityIpStyleWeight(IdMixin, TimestampMixin, Base):
    __tablename__ = "city_ip_style_weights"

    city_ip_id: Mapped[int] = mapped_column(ForeignKey("city_ips.id", ondelete="CASCADE"), index=True)
    style: Mapped[str] = mapped_column(String(32))
    weight: Mapped[int] = mapped_column(Integer, default=0)
