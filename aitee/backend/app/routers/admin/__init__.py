from typing import List
"""Admin routers 聚合。"""
from fastapi import APIRouter

from . import auth, basic_crud, products, model_channels, city_ips, orders, users, partners, stores, qrcodes

all_routers: List[APIRouter] = [
    auth.router,
    products.router,
    products.skus_router,
    *basic_crud.routers,
    model_channels.router,
    city_ips.router,
    city_ips.elements_router,
    city_ips.items_router,
    orders.router,
    users.router,
    partners.router,
    stores.router,
    qrcodes.router,
]