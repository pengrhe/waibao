"""商品 + SKU 管理：商品和 SKU 是 1:N，需要联动维护。"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import require_role
from app.models import Product, ProductSku
from app.schemas.admin import ProductIn, ProductSkuIn
from app.schemas.common import Resp

router = APIRouter(prefix="/admin/products", tags=["admin-products"])
skus_router = APIRouter(prefix="/admin/skus", tags=["admin-skus"])


def _serialize_product(p: Product, skus: List[ProductSku]) -> dict:
    return {
        "id": p.id,
        "category_id": p.category_id,
        "name": p.name,
        "subtitle": p.subtitle,
        "base_price": float(p.base_price),
        "main_image_url": p.main_image_url,
        "gallery": p.gallery,
        "description": p.description,
        "available_colors": p.available_colors,
        "available_sizes": p.available_sizes,
        "enabled": p.enabled,
        "sort": p.sort,
        "created_at": p.created_at.isoformat() if p.created_at else None,
        "updated_at": p.updated_at.isoformat() if p.updated_at else None,
        "skus": [
            {
                "id": s.id,
                "color": s.color,
                "size": s.size,
                "price": float(s.price),
                "stock": s.stock,
                "image_url": s.image_url,
                "enabled": s.enabled,
            }
            for s in skus
        ],
    }


def _load_skus(db: Session, product_id: int) -> List[ProductSku]:
    return list(db.execute(
        select(ProductSku).where(ProductSku.product_id == product_id).order_by(ProductSku.id)
    ).scalars())


@router.get("", response_model=Resp[dict])
def list_products(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    enabled: bool = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(Product)
    if keyword:
        stmt = stmt.where(Product.name.ilike(f"%{keyword}%"))
    if enabled is not None:
        stmt = stmt.where(Product.enabled == enabled)
    stmt = stmt.order_by(Product.sort, Product.id.desc())
    all_items = db.execute(stmt).scalars().all()
    total = len(all_items)
    start = (page - 1) * page_size
    items = all_items[start:start + page_size]
    return Resp(data={
        "items": [_serialize_product(p, _load_skus(db, p.id)) for p in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    })


@router.get("/{pid}", response_model=Resp[dict])
def get_product(pid: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))) -> Resp[dict]:
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="product not found")
    return Resp(data=_serialize_product(p, _load_skus(db, pid)))


@router.post("", response_model=Resp[dict])
def create_product(
    payload: ProductIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    data = payload.model_dump(exclude={"skus"})
    p = Product(**data)
    db.add(p)
    db.flush()
    for s in payload.skus:
        sku = ProductSku(product_id=p.id, **s.model_dump(exclude={"id"}))
        db.add(sku)
    db.commit()
    db.refresh(p)
    return Resp(data=_serialize_product(p, _load_skus(db, p.id)))


@router.put("/{pid}", response_model=Resp[dict])
def update_product(
    pid: int,
    payload: ProductIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="product not found")
    data = payload.model_dump(exclude={"skus"})
    for k, v in data.items():
        setattr(p, k, v)

    # 同步 SKUs：以 payload.skus 为准
    existing = {s.id: s for s in _load_skus(db, pid)}
    keep_ids = set()
    for s_in in payload.skus:
        if s_in.id and s_in.id in existing:
            sku = existing[s_in.id]
            for k, v in s_in.model_dump(exclude={"id"}).items():
                setattr(sku, k, v)
            keep_ids.add(s_in.id)
        else:
            sku = ProductSku(product_id=pid, **s_in.model_dump(exclude={"id"}))
            db.add(sku)
            db.flush()
            keep_ids.add(sku.id)
    for sid, sku in existing.items():
        if sid not in keep_ids:
            db.delete(sku)
    db.commit()
    db.refresh(p)
    return Resp(data=_serialize_product(p, _load_skus(db, pid)))


@router.delete("/{pid}", response_model=Resp[dict])
def delete_product(
    pid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="product not found")
    db.delete(p)
    db.commit()
    return Resp(data={"deleted": pid})


@router.post("/{pid}/toggle", response_model=Resp[dict])
def toggle(pid: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))) -> Resp[dict]:
    p = db.get(Product, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="product not found")
    p.enabled = not bool(p.enabled)
    db.commit()
    return Resp(data={"id": pid, "enabled": p.enabled})


# ============ 单 SKU 操作 ============

@skus_router.put("/{sid}", response_model=Resp[dict])
def update_sku(
    sid: int,
    payload: ProductSkuIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    sku = db.get(ProductSku, sid)
    if not sku:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="sku not found")
    for k, v in payload.model_dump(exclude={"id"}).items():
        setattr(sku, k, v)
    db.commit()
    return Resp(data={"id": sid, "stock": sku.stock, "price": float(sku.price), "enabled": sku.enabled})
