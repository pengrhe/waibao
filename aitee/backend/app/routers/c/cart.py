from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import CartItem, Product, ProductSku, User
from app.schemas.c import CartItemIn, CartItemOut, ProductOut, ProductSkuOut
from app.schemas.common import Resp

router = APIRouter(prefix="/cart", tags=["c-cart"])


def _enrich(db: Session, item: CartItem) -> CartItemOut:
    out = CartItemOut.model_validate(item)
    sku = db.get(ProductSku, item.sku_id)
    if sku:
        out.sku = ProductSkuOut.model_validate(sku)
        prod = db.get(Product, sku.product_id)
        if prod:
            out.product = ProductOut.model_validate(prod)
    return out


@router.get("", response_model=Resp[List[CartItemOut]])
def list_cart(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[CartItemOut]]:
    items = db.execute(
        select(CartItem).where(CartItem.user_id == user.id).order_by(CartItem.id.desc())
    ).scalars().all()
    return Resp(data=[_enrich(db, c) for c in items])


@router.post("", response_model=Resp[CartItemOut])
def add_cart(
    payload: CartItemIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[CartItemOut]:
    sku = db.get(ProductSku, payload.sku_id)
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="sku not found")

    # 同 sku + 同 design 合并数量
    existing = db.execute(
        select(CartItem).where(
            CartItem.user_id == user.id,
            CartItem.sku_id == payload.sku_id,
            CartItem.design_id == payload.design_id,
        )
    ).scalar_one_or_none()
    if existing:
        existing.qty += payload.qty
        item = existing
    else:
        item = CartItem(user_id=user.id, **payload.model_dump())
        db.add(item)
    db.commit()
    db.refresh(item)
    return Resp(data=_enrich(db, item))


class CartUpdateIn(BaseModel):
    qty: int | None = None
    selected: bool | None = None


@router.put("/{cid}", response_model=Resp[CartItemOut])
def update_cart(
    cid: int,
    payload: CartUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[CartItemOut]:
    item = db.get(CartItem, cid)
    if not item or item.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="cart item not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(item, k, v)
    if item.qty is not None and item.qty <= 0:
        db.delete(item)
        db.commit()
        return Resp(data=CartItemOut(id=cid, sku_id=item.sku_id, design_id=item.design_id, qty=0, selected=False))
    db.commit()
    db.refresh(item)
    return Resp(data=_enrich(db, item))


class CartRemoveIn(BaseModel):
    ids: List[int]


@router.post("/remove", response_model=Resp[List[CartItemOut]])
def remove_cart(
    payload: CartRemoveIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[CartItemOut]]:
    if payload.ids:
        items = db.execute(
            select(CartItem).where(CartItem.user_id == user.id, CartItem.id.in_(payload.ids))
        ).scalars().all()
        for it in items:
            db.delete(it)
        db.commit()
    remain = db.execute(
        select(CartItem).where(CartItem.user_id == user.id).order_by(CartItem.id.desc())
    ).scalars().all()
    return Resp(data=[_enrich(db, c) for c in remain])


@router.delete("/clear", response_model=Resp[dict])
def clear_cart(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[dict]:
    items = db.execute(select(CartItem).where(CartItem.user_id == user.id)).scalars().all()
    n = len(items)
    for it in items:
        db.delete(it)
    db.commit()
    return Resp(data={"cleared": n})
