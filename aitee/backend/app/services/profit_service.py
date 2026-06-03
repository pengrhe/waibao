"""分润 / 加盟店结算 mock 服务（订单 paid 时调用）。"""
from __future__ import annotations

import logging
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import Order, Partner, PayoutRecord, SettleRecord, Store

logger = logging.getLogger("aitee.profit")


def settle_paid_order(db: Session, order: Order) -> None:
    """订单进入 paid 状态后：
    - 若关联 partner：生成 payout_records（按 partner.profit_ratio）
    - 若关联 store：生成 settle_records（按 store.settle_mode 与管理费比例）
    """
    amount = Decimal(str(order.amount_total))

    if order.partner_id:
        partner = db.get(Partner, order.partner_id)
        if partner:
            ratio = Decimal(str(partner.profit_ratio or 0))
            payout = (amount * ratio).quantize(Decimal("0.01"))
            db.add(PayoutRecord(
                order_id=order.id,
                partner_id=partner.id,
                order_amount=amount,
                ratio=ratio,
                amount=payout,
                status="recorded",
            ))
            partner.balance = Decimal(str(partner.balance or 0)) + payout
            partner.total_earned = Decimal(str(partner.total_earned or 0)) + payout
            logger.info(f"partner#{partner.id} 分润 +{payout}（order={order.id}）")

    if order.store_id:
        store = db.get(Store, order.store_id)
        if store:
            ratio = Decimal(str(store.management_fee_ratio or 0))
            mgmt_fee = (amount * ratio).quantize(Decimal("0.01"))
            net = amount - mgmt_fee
            db.add(SettleRecord(
                store_id=store.id,
                mode=store.settle_mode,
                order_id=order.id,
                gross_amount=amount,
                management_fee=mgmt_fee,
                net_amount=net,
                status="recorded",
            ))
            store.balance = Decimal(str(store.balance or 0)) + net
            logger.info(f"store#{store.id} 结算 net={net} mgmt={mgmt_fee}（order={order.id}）")
