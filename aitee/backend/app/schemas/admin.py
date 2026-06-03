"""Admin 后台 schema 汇总。"""
from __future__ import annotations
from typing import List, Optional

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============ 通用 ============

class PageQuery(BaseModel):
    page: int = 1
    page_size: int = 20
    keyword: Optional[str] = None


class PageResp(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int


# ============ Product ============

class ProductSkuIn(BaseModel):
    id: Optional[int] = None
    color: str
    size: str
    price: Decimal
    stock: int = 999
    image_url: Optional[str] = None
    enabled: bool = True


class ProductIn(BaseModel):
    category_id: Optional[int] = None
    name: str
    subtitle: Optional[str] = None
    base_price: Decimal
    main_image_url: Optional[str] = None
    gallery: Optional[List[str]] = None
    description: Optional[str] = None
    available_colors: Optional[List[str]] = None
    available_sizes: Optional[List[str]] = None
    enabled: bool = True
    sort: int = 0
    skus: List[ProductSkuIn] = Field(default_factory=list)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: Optional[int] = None
    name: str
    subtitle: Optional[str] = None
    base_price: Decimal
    main_image_url: Optional[str] = None
    gallery: Optional[List[str]] = None
    description: Optional[str] = None
    available_colors: Optional[List[str]] = None
    available_sizes: Optional[List[str]] = None
    enabled: bool
    sort: int
    created_at: datetime
    updated_at: datetime
    skus: List[Any] = []


# ============ Pattern ============

class PatternIn(BaseModel):
    category_id: Optional[int] = None
    name: str
    image_url: str
    thumb_url: Optional[str] = None
    tags: Optional[List[str]] = None
    source: str = "builtin"
    enabled: bool = True
    sort: int = 0


# ============ Coupon ============

class CouponIn(BaseModel):
    name: str
    type: str  # discount/cash
    value: Decimal
    threshold: Decimal = Decimal("0")
    valid_days: int = 30
    total: int = 0
    status: str = "active"
    description: Optional[str] = None


# ============ Banner / Topic ============

class BannerIn(BaseModel):
    position: str
    title: Optional[str] = None
    image_url: str
    link_to: Optional[str] = None
    sort: int = 0
    enabled: bool = True
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class TopicIn(BaseModel):
    title: str
    subtitle: Optional[str] = None
    cover_url: Optional[str] = None
    link_to: Optional[str] = None
    items: Optional[List[Any]] = None
    sort: int = 0
    enabled: bool = True


# ============ City IP ============

class CulturalElementIn(BaseModel):
    city: str
    name: str
    category: str  # landmark/folk/symbol/food/dialect
    description: Optional[str] = None
    style_hint: Optional[str] = None
    enabled: bool = True
    sort: int = 0


class CityIpIn(BaseModel):
    city: str
    description: Optional[str] = None
    cover_url: Optional[str] = None


# ============ Model Channel ============

class ModelChannelIn(BaseModel):
    name: str
    provider: str = "openrouter"
    base_url: str = "https://openrouter.ai/api/v1"
    api_key: str
    model_name: str
    enabled: bool = True
    is_active: bool = False
    extra: Optional[dict] = None
    remark: Optional[str] = None


# ============ Users (C 端用户) ============

class CUserIn(BaseModel):
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    status: str = "active"


# ============ Partner / Store ============

class PartnerIn(BaseModel):
    username: str
    password: Optional[str] = None
    name: str
    phone: Optional[str] = None
    channel: Optional[str] = None
    profit_ratio: Decimal = Decimal("0.05")
    bank_card: Optional[str] = None
    bank_name: Optional[str] = None
    status: str = "active"


class StoreIn(BaseModel):
    username: str
    password: Optional[str] = None
    name: str
    owner: Optional[str] = None
    phone: Optional[str] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    management_fee_ratio: Decimal = Decimal("0.10")
    settle_mode: str = "unified"
    bank_card: Optional[str] = None
    bank_name: Optional[str] = None
    promotion: Optional[dict] = None
    status: str = "active"


# ============ System Config ============

class SystemConfigIn(BaseModel):
    key: str
    value: Optional[dict] = None
    description: Optional[str] = None
    category: str = "general"


# ============ QR Code ============

class QrCodeIn(BaseModel):
    type: str  # partner_split/store_order/staff_verify/city_share
    code: Optional[str] = None  # 不填自动生成
    owner_type: Optional[str] = None
    owner_id: Optional[int] = None
    target_url: str
    style: Optional[dict] = None
    enabled: bool = True


# ============ Order admin ============

class OrderUpdateIn(BaseModel):
    status: Optional[str] = None
    remark: Optional[str] = None
    pay_method: Optional[str] = None
