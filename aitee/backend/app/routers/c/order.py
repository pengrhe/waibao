from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import Order, OrderItem, User
from app.schemas.c import OrderCreateIn, OrderItemOut, OrderOut
from app.schemas.common import Resp
from app.services.order_engine import cancel, create_order, mock_pay, transit

router = APIRouter(prefix="/orders", tags=["c-order"])


def _to_out(db: Session, order: Order) -> OrderOut:
    items = db.execute(select(OrderItem).where(OrderItem.order_id == order.id)).scalars().all()
    out = OrderOut.model_validate(order)
    out.items = [OrderItemOut.model_validate(it) for it in items]
    return out


@router.get("", response_model=Resp[List[OrderOut]])
def list_orders(
    status_filter: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[OrderOut]]:
    stmt = select(Order).where(Order.user_id == user.id).order_by(Order.id.desc())
    if status_filter and status_filter != "all":
        stmt = stmt.where(Order.status == status_filter)
    items = db.execute(stmt).scalars().all()
    return Resp(data=[_to_out(db, o) for o in items])


@router.get("/{oid}", response_model=Resp[OrderOut])
def get_order(
    oid: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[OrderOut]:
    o = db.get(Order, oid)
    if not o or o.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    return Resp(data=_to_out(db, o))


@router.post("", response_model=Resp[OrderOut])
def create(
    payload: OrderCreateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[OrderOut]:
    order = create_order(
        db,
        user,
        items_input=[i.model_dump() for i in payload.items],
        cart_item_ids=payload.cart_item_ids,
        address_id=payload.address_id,
        delivery_type=payload.delivery_type,
        user_coupon_id=payload.user_coupon_id,
        category=payload.category,
        channel=payload.channel,
        store_id=payload.store_id,
        partner_id=payload.partner_id,
        remark=payload.remark,
    )
    db.commit()
    db.refresh(order)
    return Resp(data=_to_out(db, order))


class PayIn(BaseModel):
    pay_method: str = "mock"  # mock/wechat/douyin


@router.post("/{oid}/pay", response_model=Resp[OrderOut])
def pay(
    oid: int,
    payload: PayIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[OrderOut]:
    o = db.get(Order, oid)
    if not o or o.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    mock_pay(db, o, pay_method=payload.pay_method)
    db.commit()
    db.refresh(o)
    return Resp(data=_to_out(db, o))


class CancelIn(BaseModel):
    reason: Optional[str] = "用户取消"


@router.post("/{oid}/cancel", response_model=Resp[OrderOut])
def cancel_order(
    oid: int,
    payload: CancelIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[OrderOut]:
    o = db.get(Order, oid)
    if not o or o.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    cancel(db, o, reason=payload.reason or "用户取消", operator_type="user", operator_id=user.id)
    db.commit()
    db.refresh(o)
    return Resp(data=_to_out(db, o))


@router.post("/{oid}/pickup", response_model=Resp[OrderOut])
def confirm_pickup(
    oid: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[OrderOut]:
    """C 端用户自助确认取货。状态须为 printed，转 completed。"""
    o = db.get(Order, oid)
    if not o or o.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    if o.status == "printing":
        # mock 容忍：实际还在打印中也允许标完成
        transit(db, o, to_status="printed", operator_type="system", reason="mock 跳过 printed")
    transit(db, o, to_status="completed" if o.status == "printed" else "completed",
            operator_type="user", operator_id=user.id, reason="用户确认取货")
    db.commit()
    db.refresh(o)
    return Resp(data=_to_out(db, o))
