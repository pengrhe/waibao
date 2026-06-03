"""简单 CRUD：印花 / 优惠券 / banner / topic / 系统配置 / 印花分类 / 商品分类。"""
from __future__ import annotations

from app.models import (
    Banner,
    Coupon,
    Pattern,
    PatternCategory,
    ProductCategory,
    SystemConfig,
    Topic,
)
from app.routers.admin._crud import build_crud
from app.schemas.admin import (
    BannerIn,
    CouponIn,
    PatternIn,
    SystemConfigIn,
    TopicIn,
)
from pydantic import BaseModel


class CategoryIn(BaseModel):
    name: str
    slug: str
    sort: int = 0


routers = [
    build_crud(
        name="patterns",
        model=Pattern,
        schema_in=PatternIn,
        prefix="/admin/patterns",
        keyword_columns=("name",),
    ),
    build_crud(
        name="pattern-categories",
        model=PatternCategory,
        schema_in=CategoryIn,
        prefix="/admin/pattern-categories",
        keyword_columns=("name", "slug"),
    ),
    build_crud(
        name="product-categories",
        model=ProductCategory,
        schema_in=CategoryIn,
        prefix="/admin/product-categories",
        keyword_columns=("name", "slug"),
    ),
    build_crud(
        name="coupons",
        model=Coupon,
        schema_in=CouponIn,
        prefix="/admin/coupons",
        keyword_columns=("name",),
    ),
    build_crud(
        name="banners",
        model=Banner,
        schema_in=BannerIn,
        prefix="/admin/banners",
        keyword_columns=("title",),
    ),
    build_crud(
        name="topics",
        model=Topic,
        schema_in=TopicIn,
        prefix="/admin/topics",
        keyword_columns=("title",),
    ),
    build_crud(
        name="system-configs",
        model=SystemConfig,
        schema_in=SystemConfigIn,
        prefix="/admin/system-configs",
        keyword_columns=("key", "description"),
    ),
]
