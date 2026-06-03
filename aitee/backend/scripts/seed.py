"""M1 最小 seed：建测试账号 + 默认配置 + 几条样板数据。

完整 frontend mock 全量迁移见 M2 的 seed_from_frontend.py。

用法：
    .venv\\Scripts\\python.exe scripts\\seed.py            # 增量 upsert
    .venv\\Scripts\\python.exe scripts\\seed.py --reset    # 先清空再 seed
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.db import Base, SessionLocal, engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models import (  # noqa: E402
    AdminUser,
    Banner,
    CityIp,
    CityIpItem,
    CityIpStyleWeight,
    Coupon,
    CulturalElement,
    Device,
    ModelChannel,
    Partner,
    Pattern,
    PatternCategory,
    Product,
    ProductCategory,
    ProductSku,
    Store,
    StoreStaff,
    SystemConfig,
    Topic,
    User,
)

# 前端 C 端 H5 资源 base（vite dev server 端口，启动后可访问其 public 资源）
FRONTEND_ASSET_BASE = "http://localhost:8201"


def get_or_create(db, model, defaults: dict | None = None, **filters):
    instance = db.execute(select(model).filter_by(**filters)).scalar_one_or_none()
    if instance:
        return instance, False
    params = {**filters, **(defaults or {})}
    instance = model(**params)
    db.add(instance)
    db.flush()
    return instance, True


def seed_admin(db):
    a, created = get_or_create(
        db,
        AdminUser,
        defaults={
            "password_hash": hash_password("admin123"),
            "name": "总部管理员",
            "role": "admin",
        },
        username="admin",
    )
    print(f"admin: {a.username} {'(new)' if created else ''}")


def seed_model_channel(db):
    env_key = settings.OPENROUTER_API_KEY
    fallback = "sk-or-v1-PUT-YOUR-KEY-HERE"
    ch, created = get_or_create(
        db,
        ModelChannel,
        defaults={
            "provider": "openrouter",
            "base_url": settings.OPENROUTER_BASE_URL,
            "api_key": env_key or fallback,
            "model_name": settings.OPENROUTER_MODEL,
            "enabled": True,
            "is_active": True,
            "remark": "默认 OpenRouter 通道（key 由 .env OPENROUTER_API_KEY 同步）",
        },
        name="openrouter-default",
    )
    # 幂等同步：env 里有有效 key 时覆盖（方便先 seed 再填 .env 的场景）
    if env_key and ch.api_key != env_key:
        ch.api_key = env_key
        ch.base_url = settings.OPENROUTER_BASE_URL
        ch.model_name = settings.OPENROUTER_MODEL
        db.flush()
        print(f"model_channel: {ch.name} key updated from .env")
    else:
        print(f"model_channel: {ch.name} active={ch.is_active} {'(new)' if created else ''}")


def seed_users(db):
    for phone in ("13800000001", "13800000002", "13800000003"):
        u, _ = get_or_create(
            db,
            User,
            defaults={
                "nickname": f"测试用户{phone[-1]}",
                "city": "深圳" if phone.endswith("1") else "长沙",
                "status": "active",
            },
            phone=phone,
        )
    print("users: 3 ready")


def seed_partners(db):
    for i, info in enumerate(
        [
            ("p_zhang", "张联营", "18600000001", "微信朋友圈", "0.08"),
            ("p_li", "李推广", "18600000002", "抖音短视频", "0.10"),
            ("p_wang", "王分销", "18600000003", "线下地推", "0.05"),
        ],
        1,
    ):
        un, name, phone, channel, ratio = info
        get_or_create(
            db,
            Partner,
            defaults={
                "password_hash": hash_password("partner123"),
                "name": name,
                "phone": phone,
                "channel": channel,
                "profit_ratio": Decimal(ratio),
                "status": "active",
                "audited_at": datetime.now(timezone.utc),
            },
            username=un,
        )
    print("partners: 3 ready (login: partner123)")


def seed_stores_and_staff(db):
    stores_data = [
        ("s_sz01", "深圳南山旗舰店", "0.10", "unified", "深圳", "南山区"),
        ("s_cs01", "长沙五一加盟店", "0.12", "self", "长沙", "芙蓉区"),
    ]
    created_stores = []
    for un, name, mgmt, mode, city, district in stores_data:
        s, _ = get_or_create(
            db,
            Store,
            defaults={
                "password_hash": hash_password("store123"),
                "name": name,
                "owner": "店长" + name[2:4],
                "phone": "0755-12345678",
                "province": "广东" if city == "深圳" else "湖南",
                "city": city,
                "district": district,
                "address": f"{city}{district}示范街 88 号",
                "management_fee_ratio": Decimal(mgmt),
                "settle_mode": mode,
                "status": "active",
                "audited_at": datetime.now(timezone.utc),
            },
            username=un,
        )
        created_stores.append(s)
    print(f"stores: {len(created_stores)} ready (login: store123)")

    # 店员
    staff_data = [
        (created_stores[0].id, "st_sz01_a", "小王"),
        (created_stores[0].id, "st_sz01_b", "小李"),
        (created_stores[1].id, "st_cs01_a", "小张"),
    ]
    for sid, un, name in staff_data:
        get_or_create(
            db,
            StoreStaff,
            defaults={
                "password_hash": hash_password("staff123"),
                "name": name,
                "role": "staff",
            },
            store_id=sid,
            username=un,
        )
    print("staff: 3 ready (login: staff123)")

    # 设备
    devices = [
        (created_stores[0].id, "SN-SZ-001", "南山店主机"),
        (created_stores[1].id, "SN-CS-001", "长沙店主机"),
    ]
    for sid, sn, name in devices:
        get_or_create(
            db,
            Device,
            defaults={
                "name": name,
                "model": "AITEE-PRINTER-X1",
                "status": "idle",
                "ink_level": 95,
                "online": True,
                "last_heartbeat_at": datetime.now(timezone.utc),
            },
            store_id=sid,
            sn=sn,
        )
    print("devices: 2 ready")


def seed_catalog(db):
    # 商品分类
    cats = [
        ("T 恤", "tshirt"),
        ("帆布包", "tote"),
        ("卫衣", "hoodie"),
    ]
    cat_map = {}
    for name, slug in cats:
        c, _ = get_or_create(db, ProductCategory, defaults={"name": name}, slug=slug)
        cat_map[slug] = c
    print(f"product_categories: {len(cat_map)} ready")

    # 商品
    products = [
        ("经典圆领 T 恤", "tshirt", "49.00", ["white", "black", "pink", "purple"], ["S", "M", "L", "XL"]),
        ("帆布托特包", "tote", "39.00", ["natural", "black"], ["F"]),
        ("纯色卫衣", "hoodie", "129.00", ["gray", "black"], ["M", "L", "XL"]),
    ]
    for name, slug, price, colors, sizes in products:
        p, created = get_or_create(
            db,
            Product,
            defaults={
                "category_id": cat_map[slug].id,
                "base_price": Decimal(price),
                "available_colors": colors,
                "available_sizes": sizes,
                "subtitle": "可 AI 定制",
                "enabled": True,
            },
            name=name,
        )
        if created:
            for color in colors:
                for size in sizes:
                    db.add(
                        ProductSku(
                            product_id=p.id,
                            color=color,
                            size=size,
                            price=Decimal(price),
                            stock=999,
                            enabled=True,
                        )
                    )
            db.flush()
    print("products: 3 ready (+ skus)")

    # 印花分类
    p_cats = [("热门", "hot"), ("城市", "city"), ("宠物", "pet"), ("IP", "ip"), ("新品", "new")]
    pcat_map = {}
    for name, slug in p_cats:
        c, _ = get_or_create(db, PatternCategory, defaults={"name": name}, slug=slug)
        pcat_map[slug] = c
    print(f"pattern_categories: {len(pcat_map)} ready")

    # 印花（小集，路径引用 frontend public/assets/img/patterns/*.png）
    sample_patterns = [
        ("热门火焰", "hot", "hot01.png"),
        ("热门花朵", "hot", "hot02.png"),
        ("热门浪潮", "hot", "hot03.png"),
        ("城市天际线", "city", "city01.png"),
        ("城市霓虹", "city", "city02.png"),
        ("猫咪萌物", "pet", "pet01.png"),
        ("柴犬萌物", "pet", "pet02.png"),
        ("熊熊萌物", "pet", "pet03.png"),
        ("城市 IP", "ip", "ip01.png"),
        ("新品上架", "new", "new02.png"),
    ]
    for name, slug, fname in sample_patterns:
        url = f"{FRONTEND_ASSET_BASE}/assets/img/patterns/{fname}"
        get_or_create(
            db,
            Pattern,
            defaults={
                "category_id": pcat_map[slug].id,
                "image_url": url,
                "thumb_url": url,
                "source": "builtin",
                "enabled": True,
            },
            name=name,
        )
    print(f"patterns: {len(sample_patterns)} ready")


def seed_marketing(db):
    # 优惠券：新人 7.8 折
    get_or_create(
        db,
        Coupon,
        defaults={
            "type": "discount",
            "value": Decimal("0.78"),
            "threshold": Decimal("0"),
            "valid_days": 30,
            "total": 10000,
            "claimed": 0,
            "status": "active",
            "description": "新人专享 7.8 折，30 天有效",
        },
        name="新人 7.8 折",
    )

    # banner
    get_or_create(
        db,
        Banner,
        defaults={
            "title": "把灵感穿上身",
            "image_url": f"{FRONTEND_ASSET_BASE}/assets/img/home/hero.png",
            "link_to": "/editor",
            "sort": 0,
            "enabled": True,
        },
        position="home_top",
    )

    # topic
    get_or_create(
        db,
        Topic,
        defaults={
            "subtitle": "看看大家怎么定制的",
            "cover_url": None,
            "link_to": "/gallery",
            "sort": 0,
            "enabled": True,
            "items": [],
        },
        title="人气推荐",
    )
    print("marketing: 1 coupon + 1 banner + 1 topic ready")


def seed_city_ip(db):
    cities = [
        ("深圳", "改革开放窗口、科技之都"),
        ("长沙", "网红美食 + 国潮文化"),
        ("成都", "巴蜀文化 + 熊猫故乡"),
    ]
    for city, desc in cities:
        c, created = get_or_create(db, CityIp, defaults={"description": desc}, city=city)
        if created:
            # 3 类共 6 张占位（image_url 复用 patterns）
            base = f"{FRONTEND_ASSET_BASE}/assets/img/patterns"
            items = [
                ("landmark", f"{city} 地标 1", f"{base}/city01.png"),
                ("landmark", f"{city} 地标 2", f"{base}/city02.png"),
                ("folk", f"{city} 民俗 1", f"{base}/hot01.png"),
                ("folk", f"{city} 民俗 2", f"{base}/hot02.png"),
                ("symbol", f"{city} 符号 1", f"{base}/ip01.png"),
                ("symbol", f"{city} 符号 2", f"{base}/hot03.png"),
            ]
            for cat, title, url in items:
                db.add(
                    CityIpItem(
                        city_ip_id=c.id,
                        category=cat,
                        title=title,
                        image_url=url,
                        source="builtin",
                    )
                )
            for style, weight in (
                ("guochao", 40),
                ("cartoon", 30),
                ("watercolor", 20),
                ("vintage", 10),
            ):
                db.add(
                    CityIpStyleWeight(city_ip_id=c.id, style=style, weight=weight)
                )
            db.flush()
    print(f"city_ip: {len(cities)} cities ready")


def seed_cultural_elements(db):
    data = [
        ("深圳", "莲花山", "landmark"),
        ("深圳", "京基 100", "landmark"),
        ("深圳", "皮皮虾", "food"),
        ("长沙", "橘子洲", "landmark"),
        ("长沙", "茶颜悦色", "food"),
        ("长沙", "湘绣", "folk"),
        ("成都", "宽窄巷子", "landmark"),
        ("成都", "熊猫", "symbol"),
        ("成都", "火锅", "food"),
    ]
    for city, name, cat in data:
        get_or_create(
            db,
            CulturalElement,
            defaults={"category": cat, "enabled": True},
            city=city,
            name=name,
        )
    print(f"cultural_elements: {len(data)} ready")


def seed_system_configs(db):
    configs = [
        ("print_price_base", {"tshirt": 49, "tote": 39, "hoodie": 129}, "基础打印价格"),
        ("default_partner_ratio", {"value": 0.05}, "默认伙伴分润比例"),
        ("default_mgmt_fee_ratio", {"value": 0.10}, "默认加盟店管理费比例"),
        ("settle_cycle", {"value": "monthly"}, "结算周期：monthly/weekly"),
        (
            "channel_switches",
            {"h5": True, "wx_app": True, "dy_app": True, "offline_store": True},
            "多端功能开关",
        ),
        (
            "ai_styles",
            ["cartoon", "realistic", "vintage", "guochao", "watercolor"],
            "AI 出图可选风格",
        ),
    ]
    for key, value, desc in configs:
        get_or_create(
            db,
            SystemConfig,
            defaults={"value": value, "description": desc, "category": "general"},
            key=key,
        )
    print(f"system_configs: {len(configs)} ready")


def main(reset: bool = False) -> None:
    if reset:
        print("!! reset: dropping & recreating all tables")
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        seed_admin(db)
        seed_model_channel(db)
        seed_users(db)
        seed_partners(db)
        seed_stores_and_staff(db)
        seed_catalog(db)
        seed_marketing(db)
        seed_city_ip(db)
        seed_cultural_elements(db)
        seed_system_configs(db)
        db.commit()
        print("\nseed done.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="drop & recreate tables before seed")
    args = parser.parse_args()
    main(reset=args.reset)
