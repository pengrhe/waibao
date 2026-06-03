"""C 端 API schema 汇总（对齐 frontend src/api/* 接口签名）。"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============== 通用 ==============

class IdName(BaseModel):
    id: int
    name: str


# ============== users / addresses ==============

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    city: Optional[str] = None
    status: str = "active"


class CLoginIn(BaseModel):
    """C 端 mock 登录（M2 用，M3 接真微信/抖音）。"""
    channel: str = "h5"  # h5/wx_app/dy_app
    code: Optional[str] = None  # 真登录时的临时 code
    phone: Optional[str] = None  # mock 模式直接填手机号
    nickname: Optional[str] = None


class CLoginOut(BaseModel):
    token: str
    user: UserProfile


class AddressIn(BaseModel):
    receiver: str
    phone: str
    province: str
    city: str
    district: str
    detail: str
    is_default: bool = False


class AddressOut(AddressIn):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ============== coupons ==============

class CouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    type: str  # discount/cash
    value: Decimal
    threshold: Decimal
    valid_days: int
    description: Optional[str] = None


class UserCouponOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    coupon_id: int
    coupon: CouponOut
    status: str  # unused/used/expired
    claimed_at: datetime
    expire_at: Optional[datetime] = None


# ============== products / patterns ==============

class ProductSkuOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    color: str
    size: str
    price: Decimal
    stock: int
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: Optional[int] = None
    name: str
    subtitle: Optional[str] = None
    base_price: Decimal
    main_image_url: Optional[str] = None
    gallery: Optional[List[str]] = None
    available_colors: Optional[List[str]] = None
    available_sizes: Optional[List[str]] = None
    description: Optional[str] = None
    skus: List[ProductSkuOut] = []


class PatternCategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str


class PatternOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category_id: Optional[int] = None
    name: str
    image_url: str
    thumb_url: Optional[str] = None
    tags: Optional[List[str]] = None
    source: str = "builtin"


# ============== designs / cart ==============

class DesignIn(BaseModel):
    name: str = "未命名设计"
    product_id: Optional[int] = None
    sku_id: Optional[int] = None
    side: str = "front"
    layers: Optional[List[Any]] = None
    preview_url: Optional[str] = None


class DesignOut(DesignIn):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    created_at: datetime
    updated_at: datetime


class CartItemIn(BaseModel):
    sku_id: int
    qty: int = 1
    design_id: Optional[int] = None
    snapshot: Optional[dict] = None


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku_id: int
    design_id: Optional[int] = None
    qty: int
    selected: bool
    snapshot: Optional[dict] = None
    sku: Optional[ProductSkuOut] = None
    product: Optional[ProductOut] = None


# ============== orders ==============

class OrderItemIn(BaseModel):
    sku_id: Optional[int] = None
    design_id: Optional[int] = None
    qty: int = 1
    snapshot: Optional[dict] = None


class OrderCreateIn(BaseModel):
    items: List[OrderItemIn] = Field(default_factory=list)
    cart_item_ids: Optional[List[int]] = None  # 从购物车结算
    address_id: Optional[int] = None
    delivery_type: str = "pickup"  # pickup/express
    user_coupon_id: Optional[int] = None
    category: str = "personal"
    channel: str = "h5"
    store_id: Optional[int] = None
    partner_id: Optional[int] = None
    remark: Optional[str] = None


class OrderItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name_snapshot: str
    color_snapshot: Optional[str] = None
    size_snapshot: Optional[str] = None
    preview_url: Optional[str] = None
    unit_price: Decimal
    qty: int
    subtotal: Decimal


class OrderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    order_no: str
    user_id: Optional[int] = None
    category: str
    channel: str
    store_id: Optional[int] = None
    partner_id: Optional[int] = None
    address_id: Optional[int] = None
    delivery_type: str
    amount_goods: Decimal
    amount_shipping: Decimal
    amount_discount: Decimal
    amount_total: Decimal
    status: str
    pay_method: Optional[str] = None
    paid_at: Optional[datetime] = None
    canceled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut] = []


# ============== home / city / banners / topics ==============

class BannerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    position: str
    title: Optional[str] = None
    image_url: str
    link_to: Optional[str] = None
    sort: int = 0


class TopicOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    subtitle: Optional[str] = None
    cover_url: Optional[str] = None
    link_to: Optional[str] = None
    items: Optional[List[Any]] = None
    sort: int = 0


class CityIpItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    category: str
    title: str
    image_url: str


class CityIpOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    city: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    items: List[CityIpItemOut] = []
    elements: List[str] = []  # 来自 cultural_elements 名称
    total_count: int = 0


# ============== AI ==============

class AiGenerateIn(BaseModel):
    type: str = "t2i"  # t2i/i2i/ti2i
    prompt: Optional[str] = None
    style: Optional[str] = None
    source_image_url: Optional[str] = None
    n: int = 4


class AiSampleOut(BaseModel):
    id: int
    image_url: str
    thumb_url: Optional[str] = None
    prompt: Optional[str] = None
    style: Optional[str] = None


class AiGenerateOut(BaseModel):
    samples: List[AiSampleOut]
    status: str = "success"
    fallback: bool = False  # True 表示走了 mock fallback
