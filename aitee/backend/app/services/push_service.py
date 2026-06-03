"""Mock 推送服务：仅写 push_messages 表（站内信），channel=wechat_notify/inapp 等。

真接入：channel=wechat_notify 时调微信订阅消息；douyin 走抖音消息接口。
M2 全 mock：只记录，C 端通过 /api/v1/messages 读取。
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models import PushMessage

logger = logging.getLogger("aitee.push")


def push(
    db: Session,
    *,
    user_type: str,
    user_id: int,
    title: str,
    body: Optional[str] = None,
    channel: str = "inapp",
    template: Optional[str] = None,
    link_to: Optional[str] = None,
    payload: Optional[dict] = None,
) -> PushMessage:
    msg = PushMessage(
        user_type=user_type,
        user_id=user_id,
        channel=channel,
        template=template,
        title=title,
        body=body,
        link_to=link_to,
        payload=payload,
        status="sent",
        sent_at=datetime.now(timezone.utc),
    )
    db.add(msg)
    db.flush()
    logger.info(f"[mock-push] {channel} → {user_type}#{user_id}: {title}")
    return msg


def push_order_status(db: Session, order, prev: str, new: str) -> None:
    """订单状态切换时给 C 端用户发提醒。"""
    if not order.user_id:
        return
    templates = {
        "paid": ("支付成功", f"订单 {order.order_no} 已支付，请等待打印"),
        "pending_print": ("正在排版", f"订单 {order.order_no} 已派给设备"),
        "printing": ("正在打印", f"订单 {order.order_no} 设备已开机"),
        "printed": ("打印完成", f"订单 {order.order_no} 可以取货啦"),
        "completed": ("订单已完成", f"订单 {order.order_no} 已完成，期待您的下次光临"),
        "canceled": ("订单已取消", f"订单 {order.order_no} 已取消"),
        "refunded": ("退款已发起", f"订单 {order.order_no} 退款处理中"),
    }
    t = templates.get(new)
    if not t:
        return
    push(
        db,
        user_type="c_user",
        user_id=order.user_id,
        title=t[0],
        body=t[1],
        channel="wechat_notify",
        template=f"order_{new}",
        link_to=f"/pages/order-detail/index?id={order.id}",
        payload={"order_id": order.id, "order_no": order.order_no, "status": new},
    )


def push_to_partner(db: Session, *, partner_id: int, title: str, body: str) -> None:
    push(db, user_type="partner", user_id=partner_id, title=title, body=body, channel="inapp")


def push_to_store(db: Session, *, store_id: int, title: str, body: str, link_to: Optional[str] = None) -> None:
    push(db, user_type="store", user_id=store_id, title=title, body=body, channel="inapp", link_to=link_to)
