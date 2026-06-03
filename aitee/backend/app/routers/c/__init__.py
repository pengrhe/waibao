from typing import List
"""C 端 API routers 聚合。所有 /api/v1/* （非 admin/partner/store/staff）路由在此挂载。"""
from fastapi import APIRouter

from . import auth, user, address, coupon, product, pattern, design, cart, order, home, city, ai, messages, qrcode

# 统一 prefix 在主 app 里加，这里只聚合
all_routers: List[APIRouter] = [
    auth.router,
    user.router,
    address.router,
    coupon.router,
    product.router,
    pattern.router,
    design.router,
    cart.router,
    order.router,
    home.router,
    city.router,
    ai.router,
    messages.router,
    qrcode.router,
]