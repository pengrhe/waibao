"""订单引擎：创建 / 状态机 / 取消 / 退款 / 计算金额。"""
from __future__ import annotations

import random
import string
from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Address,
    CartItem,
    Order,
    OrderItem,
    OrderStatusLog,
    Product,
    ProductSku,
    User,
    UserCoupon,
)


# 状态机定义
TRANSITIONS: Dict[str, Set[str]] = {
    "pending_pay": {"paid", "canceled"},
    "paid": {"pending_print", "refunded"},
    "pending_print": {"printing", "canceled", "refunded"},
    "printing": {"printed", "refunded"},
    "printed": {"picked", "completed"},
    "picked": {"completed"},
    "completed": set(),
    "canceled": set(),
    "refunded": set(),
}


def can_transit(frm: str, to: str) -> bool:
    return to in TRANSITIONS.get(frm, set())


def gen_order_no() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    rand = "".join(random.choices(string.digits, k=4))
    return f"AT{ts}{rand}"


def _apply_coupon(total: Decimal, user_coupon: Optional[UserCoupon]) -> Tuple[Decimal, Decimal]:
    """返回 (折扣金额 discount, 实付 amount_total)。"""
    if not user_coupon or user_coupon.status != "unused":
        return Decimal("0"), total
    c = user_coupon.coupon
    if total < c.threshold:
        return Decimal("0"), total
    if c.type == "cash":
        discount = min(c.value, total)
    else:  # discount：value 是折扣率，比如 0.78 表示打 78 折
        discount = (total * (Decimal("1") - c.value)).quantize(Decimal("0.01"))
    final = max(Decimal("0"), total - discount)
    return discount, final


def create_order(
    db: Session,
    user: User,
    *,
    items_input: List[dict],
    cart_item_ids: Optional[List[int]] = None,
    address_id: Optional[int] = None,
    delivery_type: str = "pickup",
    user_coupon_id: Optional[int] = None,
    category: str = "personal",
    channel: str = "h5",
    store_id: Optional[int] = None,
    partner_id: Optional[int] = None,
    remark: Optional[str] = None,
) -> Order:
    """创建订单。items_input 为 [{sku_id, qty, design_id, snapshot}]，可与 cart_item_ids 二选一。"""

    # 合并：优先用 items_input；否则从购物车取
    resolved: List[Tuple[ProductSku, int, Optional[int], Optional[dict]]] = []
    cart_to_clear: List[int] = []

    if cart_item_ids:
        cart_items = db.execute(
            select(CartItem).where(CartItem.user_id == user.id, CartItem.id.in_(cart_item_ids))
        ).scalars().all()
        if not cart_items:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="购物车项不存在")
        for ci in cart_items:
            sku = db.get(ProductSku, ci.sku_id)
            if not sku:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"sku {ci.sku_id} 已下架")
            resolved.append((sku, ci.qty, ci.design_id, ci.snapshot))
            cart_to_clear.append(ci.id)
    else:
        if not items_input:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="订单为空")
        for it in items_input:
            sku = db.get(ProductSku, it["sku_id"])
            if not sku:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"sku {it.get('sku_id')} 不存在")
            qty = int(it.get("qty", 1))
            resolved.append((sku, qty, it.get("design_id"), it.get("snapshot")))

    # 校验地址（非自提需要）
    if delivery_type != "pickup":
        if not address_id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="请选择地址")
        addr = db.get(Address, address_id)
        if not addr or addr.user_id != user.id:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="地址不存在")

    # 校验优惠券
    uc: Optional[UserCoupon] = None
    if user_coupon_id:
        uc = db.get(UserCoupon, user_coupon_id)
        if not uc or uc.user_id != user.id or uc.status != "unused":
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="优惠券不可用")

    # 计算金额
    amount_goods = Decimal("0")
    order_items: List[OrderItem] = []
    for sku, qty, design_id, snapshot in resolved:
        prod = db.get(Product, sku.product_id)
        if not prod:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="商品已下架")
        if sku.stock < qty:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail=f"{prod.name} 库存不足")
        subtotal = sku.price * qty
        amount_goods += subtotal
        order_items.append(
            OrderItem(
                product_id=prod.id,
                sku_id=sku.id,
                design_id=design_id,
                name_snapshot=prod.name,
                color_snapshot=sku.color,
                size_snapshot=sku.size,
                preview_url=(snapshot or {}).get("preview_url") if snapshot else None,
                unit_price=sku.price,
                qty=qty,
                subtotal=subtotal,
            )
        )

    amount_shipping = Decimal("0")  # M2 mock 包邮
    discount, amount_total = _apply_coupon(amount_goods + amount_shipping, uc)

    # 创建 Order
    order = Order(
        order_no=gen_order_no(),
        user_id=user.id,
        category=category,
        channel=channel,
        store_id=store_id,
        partner_id=partner_id,
        address_id=address_id,
        delivery_type=delivery_type,
        amount_goods=amount_goods,
        amount_shipping=amount_shipping,
        amount_discount=discount,
        amount_total=amount_total,
        coupon_id=uc.id if uc else None,
        status="pending_pay",
        remark=remark,
    )
    db.add(order)
    db.flush()

    for oi in order_items:
        oi.order_id = order.id
        db.add(oi)

    # 扣库存 + 锁券
    for sku, qty, _, _ in resolved:
        sku.stock -= qty
    if uc:
        uc.order_id = order.id

    # 清购物车
    for cid in cart_to_clear:
        ci = db.get(CartItem, cid)
        if ci:
            db.delete(ci)

    # 状态日志
    db.add(OrderStatusLog(
        order_id=order.id,
        from_status=None,
        to_status="pending_pay",
        operator_type="user",
        operator_id=user.id,
        reason="创建订单",
    ))

    db.flush()
    return order


def transit(
    db: Session,
    order: Order,
    *,
    to_status: str,
    operator_type: str = "system",
    operator_id: Optional[int] = None,
    reason: Optional[str] = None,
    extra: Optional[dict] = None,
) -> Order:
    """通用状态推进。"""
    if not can_transit(order.status, to_status):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail=f"非法状态切换：{order.status} → {to_status}",
        )
    from_status = order.status
    order.status = to_status
    now = datetime.now(timezone.utc)
    if to_status == "paid":
        order.paid_at = now
    elif to_status == "canceled":
        order.canceled_at = now
    elif to_status == "completed":
        order.completed_at = now

    db.add(OrderStatusLog(
        order_id=order.id,
        from_status=from_status,
        to_status=to_status,
        operator_type=operator_type,
        operator_id=operator_id,
        reason=reason,
    ))
    db.flush()

    # 副作用：推送 + 分账（仅 paid 阶段计分账）
    try:
        from app.services.push_service import push_order_status
        push_order_status(db, order, from_status or "", to_status)
    except Exception:  # noqa: BLE001
        pass
    if to_status == "paid":
        try:
            from app.services.profit_service import settle_paid_order
            settle_paid_order(db, order)
        except Exception:  # noqa: BLE001
            pass

    return order


def mock_pay(
    db: Session,
    order: Order,
    *,
    pay_method: str = "mock",
    auto_advance: bool = True,
) -> Order:
    """mock 支付：立即变 paid，可选自动推进到 pending_print。"""
    if order.status != "pending_pay":
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="订单状态不可支付")
    order.pay_method = pay_method
    transit(db, order, to_status="paid", operator_type="user", operator_id=order.user_id, reason=f"mock 支付 {pay_method}")
    if auto_advance:
        transit(db, order, to_status="pending_print", operator_type="system", reason="自动派发打印")
    # 使用优惠券
    if order.coupon_id:
        uc = db.get(UserCoupon, order.coupon_id)
        if uc and uc.status == "unused":
            uc.status = "used"
            uc.used_at = datetime.now(timezone.utc)
    return order


def cancel(
    db: Session,
    order: Order,
    *,
    reason: str = "用户取消",
    operator_type: str = "user",
    operator_id: Optional[int] = None,
) -> Order:
    """取消 / 退款：回滚库存 + 退券。"""
    if order.status in ("completed", "canceled", "refunded"):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="订单不可取消")
    target = "canceled" if order.status in ("pending_pay", "pending_print") else "refunded"
    transit(db, order, to_status=target, operator_type=operator_type, operator_id=operator_id, reason=reason)

    # 回滚库存
    items = db.execute(select(OrderItem).where(OrderItem.order_id == order.id)).scalars().all()
    for oi in items:
        if oi.sku_id:
            sku = db.get(ProductSku, oi.sku_id)
            if sku:
                sku.stock += oi.qty

    # 退券
    if order.coupon_id:
        uc = db.get(UserCoupon, order.coupon_id)
        if uc and uc.status == "used":
            uc.status = "unused"
            uc.used_at = None
    return order
