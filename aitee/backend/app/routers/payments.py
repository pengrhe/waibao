"""Mock 支付回调（webhook）。

真接入：
- 微信：商户号→签名校验→订单号→修改状态
- 抖音：抖音支付回调（小雪花）

M2 全 mock：外部模拟工具直接调本端 webhook，按 order_no 找单子推 paid。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Order
from app.schemas.common import Resp
from app.services.order_engine import mock_pay

router = APIRouter(prefix="/payments", tags=["payments"])


class PayNotifyIn(BaseModel):
    order_no: str
    success: bool = True
    pay_method: str = "mock"  # wechat/douyin/mock


@router.post("/wechat/notify", response_model=Resp[dict])
def wechat_notify(payload: PayNotifyIn, db: Session = Depends(get_db)) -> Resp[dict]:
    return _handle_notify(db, payload, default_method="wechat")


@router.post("/douyin/notify", response_model=Resp[dict])
def douyin_notify(payload: PayNotifyIn, db: Session = Depends(get_db)) -> Resp[dict]:
    return _handle_notify(db, payload, default_method="douyin")


@router.post("/mock/notify", response_model=Resp[dict])
def mock_notify(payload: PayNotifyIn, db: Session = Depends(get_db)) -> Resp[dict]:
    return _handle_notify(db, payload, default_method="mock")


def _handle_notify(db: Session, payload: PayNotifyIn, default_method: str) -> Resp[dict]:
    o = db.execute(select(Order).where(Order.order_no == payload.order_no)).scalar_one_or_none()
    if not o:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="order not found")
    if not payload.success:
        return Resp(data={"order_id": o.id, "status": o.status, "ok": False, "msg": "支付失败"})
    if o.status != "pending_pay":
        return Resp(data={"order_id": o.id, "status": o.status, "ok": False, "msg": "订单状态已变更"})
    mock_pay(db, o, pay_method=payload.pay_method or default_method)
    db.commit()
    return Resp(data={"order_id": o.id, "status": o.status, "ok": True})
