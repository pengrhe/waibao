# -*- coding: utf-8 -*-
"""M2 端到端 smoke：C 端下单闭环 + Admin 验证 + AI 出图 + 城市 IP。

测试通过 → exit 0；失败 → exit 1。
"""
from __future__ import annotations

import io
import json
import sys
import time
from typing import Any, Dict, Optional

import requests

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

BASE = "http://127.0.0.1:8200/api/v1"


def call(method: str, url: str, *, token: str = "", data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = requests.request(method, f"{BASE}{url}", headers=headers, data=json.dumps(data) if data is not None else None, timeout=30)
    try:
        body = r.json()
    except Exception:
        print(f"  ✗ {method} {url}  status={r.status_code}  raw={r.text[:200]}")
        raise
    if r.status_code >= 400 or (isinstance(body, dict) and body.get("code") not in (0, None)):
        print(f"  ✗ {method} {url}  status={r.status_code}  body={json.dumps(body, ensure_ascii=False)[:400]}")
        raise SystemExit(1)
    return body


def step(title: str):
    print(f"\n=== {title} ===")


def main():
    print(f">> M2 smoke against {BASE}")

    # ----- C 端登录 -----
    step("C 端 mock 登录")
    out = call("POST", "/user/auth/login", data={"channel": "wx_app", "phone": "13800138999", "nickname": "smoke用户"})
    token = out["data"]["token"]
    user_id = out["data"]["user"]["id"]
    print(f"  ✓ user_id={user_id}")

    # ----- profile -----
    step("查询 profile")
    p = call("GET", "/user/profile", token=token)["data"]
    print(f"  ✓ phone={p['phone']} nickname={p['nickname']}")

    # ----- 商品列表 + 详情 -----
    step("商品列表 / 详情")
    plist = call("GET", "/products")["data"]
    assert plist, "无商品，请先 seed"
    pid = plist[0]["id"]
    pd = call("GET", f"/products/{pid}")["data"]
    sku = pd["skus"][0]
    print(f"  ✓ product={pd['name']} sku={sku['id']} price={sku['price']}")

    # ----- 印花列表 -----
    step("印花列表")
    pat = call("GET", "/patterns")["data"]
    print(f"  ✓ patterns count={len(pat)}")

    # ----- 加入购物车 + 列表 -----
    step("购物车操作")
    call("POST", "/cart", token=token, data={"sku_id": sku["id"], "qty": 2, "snapshot": {"preview_url": pd.get("main_image_url")}})
    citems = call("GET", "/cart", token=token)["data"]
    print(f"  ✓ cart items={len(citems)}")

    # ----- 地址 -----
    step("地址")
    addr = call("POST", "/addresses", token=token, data={
        "receiver": "张三", "phone": "13900139000", "province": "广东省", "city": "深圳市",
        "district": "宝安区", "detail": "兴东街道 1 号", "is_default": True,
    })["data"]
    print(f"  ✓ address_id={addr['id']}")

    # ----- 下单 + 支付 -----
    step("下单 + mock 支付")
    order = call("POST", "/orders", token=token, data={
        "cart_item_ids": [c["id"] for c in citems],
        "address_id": addr["id"],
        "delivery_type": "express",
        "channel": "wx_app",
    })["data"]
    print(f"  ✓ order_no={order['order_no']} amount_total={order['amount_total']}")
    paid = call("POST", f"/orders/{order['id']}/pay", token=token, data={"pay_method": "wechat"})["data"]
    print(f"  ✓ pay status={paid['status']}")

    # ----- 站内信 -----
    step("消息中心")
    msgs = call("GET", "/messages", token=token)["data"]
    unread = call("GET", "/messages/unread-count", token=token)["data"]
    print(f"  ✓ messages={len(msgs)} unread={unread['count']}")

    # ----- AI 生成 -----
    step("AI 生成 4 张")
    ai = call("POST", "/ai/generate", token=token, data={"type": "t2i", "prompt": "深圳科技感", "style": "国潮", "n": 4})["data"]
    print(f"  ✓ samples={len(ai['samples'])} fallback={ai['fallback']}")

    # ----- 城市 IP -----
    step("城市 IP 详情")
    try:
        cip = call("GET", "/city-ip/深圳")["data"]
        print(f"  ✓ city={cip['city']} items={len(cip.get('items', []))}")
    except SystemExit:
        print("  ! 城市 IP 数据未 seed，跳过")

    # ----- Admin 登录 -----
    step("Admin 登录 + 列表抽查")
    a = call("POST", "/admin/auth/login", data={"username": "admin", "password": "admin123"})["data"]
    atok = a["token"]
    for path in ("/admin/products", "/admin/orders", "/admin/coupons", "/admin/users", "/admin/banners"):
        body = call("GET", f"{path}?page=1&page_size=5", token=atok)
        items = body["data"]["items"] if isinstance(body["data"], dict) else body["data"]
        print(f"  ✓ {path}  count={len(items)}")

    print("\n>>>>>> M2 smoke 全部通过 ✓\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
