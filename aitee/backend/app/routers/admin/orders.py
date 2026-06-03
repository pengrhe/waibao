"""Admin 订单管理：列表筛选 + 详情 + 状态调整 + Excel 导出 + 退款。"""
from __future__ import annotations

import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import require_role
from app.models import Order, OrderItem, OrderStatusLog, User
from app.schemas.common import Resp
from app.services.order_engine import cancel, transit

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


def _to_dict(o: Order, items: list, user: Optional[User] = None) -> dict:
    return {
        "id": o.id,
        "order_no": o.order_no,
        "user_id": o.user_id,
        "user_phone": user.phone if user else None,
        "user_nickname": user.nickname if user else None,
        "category": o.category,
        "channel": o.channel,
        "store_id": o.store_id,
        "partner_id": o.partner_id,
        "delivery_type": o.delivery_type,
        "amount_goods": float(o.amount_goods),
        "amount_shipping": float(o.amount_shipping),
        "amount_discount": float(o.amount_discount),
        "amount_total": float(o.amount_total),
        "status": o.status,
        "pay_method": o.pay_method,
        "paid_at": o.paid_at.isoformat() if o.paid_at else None,
        "canceled_at": o.canceled_at.isoformat() if o.canceled_at else None,
        "completed_at": o.completed_at.isoformat() if o.completed_at else None,
        "remark": o.remark,
        "created_at": o.created_at.isoformat() if o.created_at else None,
        "items": [
            {
                "id": it.id,
                "name": it.name_snapshot,
                "color": it.color_snapshot,
                "size": it.size_snapshot,
                "preview_url": it.preview_url,
                "unit_price": float(it.unit_price),
                "qty": it.qty,
                "subtotal": float(it.subtotal),
            }
            for it in items
        ],
    }


@router.get("", response_model=Resp[dict])
def list_orders(
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    channel: Optional[str] = None,
    category: Optional[str] = None,
    store_id: Optional[int] = None,
    partner_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(Order).order_by(Order.id.desc())
    conds = []
    if keyword:
        conds.append(or_(Order.order_no.ilike(f"%{keyword}%"), Order.remark.ilike(f"%{keyword}%")))
    if status_filter:
        conds.append(Order.status == status_filter)
    if channel:
        conds.append(Order.channel == channel)
    if category:
        conds.append(Order.category == category)
    if store_id:
        conds.append(Order.store_id == store_id)
    if partner_id:
        conds.append(Order.partner_id == partner_id)
    if start_date:
        conds.append(Order.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        conds.append(Order.created_at <= datetime.fromisoformat(end_date))
    if conds:
        stmt = stmt.where(and_(*conds))

    all_items = db.execute(stmt).scalars().all()
    total = len(all_items)
    start = (page - 1) * page_size
    page_items = all_items[start:start + page_size]

    user_ids = {o.user_id for o in page_items if o.user_id}
    users_by_id = {u.id: u for u in db.execute(select(User).where(User.id.in_(user_ids))).scalars()} if user_ids else {}

    out_items = []
    for o in page_items:
        items = list(db.execute(select(OrderItem).where(OrderItem.order_id == o.id)).scalars())
        out_items.append(_to_dict(o, items, users_by_id.get(o.user_id)))

    return Resp(data={"items": out_items, "total": total, "page": page, "page_size": page_size})


@router.get("/{oid}", response_model=Resp[dict])
def get_order(
    oid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    o = db.get(Order, oid)
    if not o:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    items = list(db.execute(select(OrderItem).where(OrderItem.order_id == o.id)).scalars())
    user = db.get(User, o.user_id) if o.user_id else None
    out = _to_dict(o, items, user)
    out["logs"] = [
        {"from": l.from_status, "to": l.to_status, "by": l.operator_type, "reason": l.reason,
         "at": l.created_at.isoformat() if l.created_at else None}
        for l in db.execute(select(OrderStatusLog).where(OrderStatusLog.order_id == oid).order_by(OrderStatusLog.id)).scalars()
    ]
    return Resp(data=out)


class StatusIn(BaseModel):
    status: str
    reason: Optional[str] = "admin 调整"


@router.post("/{oid}/status", response_model=Resp[dict])
def change_status(
    oid: int,
    payload: StatusIn,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
) -> Resp[dict]:
    o = db.get(Order, oid)
    if not o:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    transit(db, o, to_status=payload.status, operator_type="admin",
            operator_id=int(admin.get("sub", 0)) if admin.get("sub", "").isdigit() else None,
            reason=payload.reason)
    db.commit()
    return Resp(data={"id": oid, "status": o.status})


class RefundIn(BaseModel):
    reason: str = "admin 退款"


@router.post("/{oid}/refund", response_model=Resp[dict])
def refund_order(
    oid: int,
    payload: RefundIn,
    db: Session = Depends(get_db),
    admin: dict = Depends(require_role("admin")),
) -> Resp[dict]:
    o = db.get(Order, oid)
    if not o:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    cancel(db, o, reason=payload.reason, operator_type="admin")
    db.commit()
    return Resp(data={"id": oid, "status": o.status})


@router.get("/export.csv")
def export_csv(
    keyword: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
):
    """导出 CSV（不依赖 openpyxl，前端可直接保存为 Excel 打开）。"""
    stmt = select(Order).order_by(Order.id.desc())
    if keyword:
        stmt = stmt.where(or_(Order.order_no.ilike(f"%{keyword}%"), Order.remark.ilike(f"%{keyword}%")))
    if status_filter:
        stmt = stmt.where(Order.status == status_filter)
    orders = db.execute(stmt).scalars().all()

    headers = ["订单号", "状态", "渠道", "分类", "金额", "优惠", "实付", "创建时间", "支付时间", "完成时间"]
    buf = io.StringIO()
    buf.write("\ufeff")  # BOM 让 Excel 识别 UTF-8
    buf.write(",".join(headers) + "\n")
    for o in orders:
        row = [
            o.order_no,
            o.status,
            o.channel,
            o.category,
            f"{float(o.amount_goods):.2f}",
            f"{float(o.amount_discount):.2f}",
            f"{float(o.amount_total):.2f}",
            o.created_at.isoformat() if o.created_at else "",
            o.paid_at.isoformat() if o.paid_at else "",
            o.completed_at.isoformat() if o.completed_at else "",
        ]
        buf.write(",".join(f'"{c}"' for c in row) + "\n")

    data = buf.getvalue().encode("utf-8")
    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=orders.csv"},
    )
