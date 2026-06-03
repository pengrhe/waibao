from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import Coupon, User, UserCoupon
from app.schemas.c import CouponOut, UserCouponOut
from app.schemas.common import Resp

router = APIRouter(prefix="/coupons", tags=["c-coupon"])


def _refresh_status(uc: UserCoupon) -> UserCoupon:
    if uc.status == "unused" and uc.expire_at and uc.expire_at < datetime.now(timezone.utc):
        uc.status = "expired"
    return uc


@router.get("/templates", response_model=Resp[List[CouponOut]])
def list_templates(db: Session = Depends(get_db)) -> Resp[List[CouponOut]]:
    """所有可领取的优惠券模板。"""
    items = db.execute(
        select(Coupon).where(Coupon.status == "active").order_by(Coupon.id.desc())
    ).scalars().all()
    return Resp(data=[CouponOut.model_validate(c) for c in items])


@router.get("/mine", response_model=Resp[List[UserCouponOut]])
def list_mine(
    status_filter: Optional[str] = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[UserCouponOut]]:
    items = db.execute(
        select(UserCoupon).where(UserCoupon.user_id == user.id).order_by(UserCoupon.id.desc())
    ).scalars().all()
    for uc in items:
        _refresh_status(uc)
    db.commit()
    if status_filter:
        items = [uc for uc in items if uc.status == status_filter]
    return Resp(data=[UserCouponOut.model_validate(uc) for uc in items])


@router.post("/claim/{coupon_id}", response_model=Resp[UserCouponOut])
def claim(
    coupon_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[UserCouponOut]:
    coupon = db.get(Coupon, coupon_id)
    if not coupon or coupon.status != "active":
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="coupon not available")
    if coupon.total and coupon.claimed >= coupon.total:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="券已领完")

    now = datetime.now(timezone.utc)
    uc = UserCoupon(
        user_id=user.id,
        coupon_id=coupon.id,
        status="unused",
        claimed_at=now,
        expire_at=now + timedelta(days=coupon.valid_days),
    )
    coupon.claimed += 1
    db.add(uc)
    db.commit()
    db.refresh(uc)
    return Resp(data=UserCouponOut.model_validate(uc))


@router.get("/best/{amount}", response_model=Resp[Optional[UserCouponOut]])
def best_for_amount(
    amount: float,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[Optional[UserCouponOut]]:
    """给定金额返回最优可用券。"""
    items = db.execute(
        select(UserCoupon).where(UserCoupon.user_id == user.id, UserCoupon.status == "unused")
    ).scalars().all()
    amt = Decimal(str(amount))
    best: UserCoupon | None = None
    best_save = Decimal("0")
    for uc in items:
        _refresh_status(uc)
        if uc.status != "unused" or amt < uc.coupon.threshold:
            continue
        if uc.coupon.type == "cash":
            save = uc.coupon.value
        else:  # discount (0.78 = 78 折)
            save = amt * (Decimal("1") - uc.coupon.value)
        if save > best_save:
            best_save = save
            best = uc
    db.commit()
    return Resp(data=UserCouponOut.model_validate(best) if best else None)
