from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Product, ProductCategory, ProductSku
from app.schemas.c import ProductOut, ProductSkuOut
from app.schemas.common import Resp
from app.services.mockup import product_mockup

router = APIRouter(prefix="/products", tags=["c-product"])


@router.get("/categories", response_model=Resp[List[dict]])
def list_categories(db: Session = Depends(get_db)) -> Resp[List[dict]]:
    items = db.execute(
        select(ProductCategory).order_by(ProductCategory.sort, ProductCategory.id)
    ).scalars().all()
    return Resp(data=[{"id": c.id, "name": c.name, "slug": c.slug} for c in items])


@router.get("", response_model=Resp[List[ProductOut]])
def list_products(
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
) -> Resp[List[ProductOut]]:
    stmt = select(Product).where(Product.enabled == True).order_by(Product.sort, Product.id)  # noqa: E712
    if category_id:
        stmt = stmt.where(Product.category_id == category_id)
    items = db.execute(stmt).scalars().all()
    out: List[ProductOut] = []
    for p in items:
        skus = list(
            db.execute(
                select(ProductSku).where(ProductSku.product_id == p.id, ProductSku.enabled == True)  # noqa: E712
            ).scalars()
        )
        po = ProductOut.model_validate(p)
        po.skus = [ProductSkuOut.model_validate(s) for s in skus]
        out.append(po)
    return Resp(data=out)


@router.get("/{pid}", response_model=Resp[ProductOut])
def get_product(pid: int, db: Session = Depends(get_db)) -> Resp[ProductOut]:
    p = db.get(Product, pid)
    if not p or not p.enabled:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="product not found")
    skus = list(
        db.execute(
            select(ProductSku).where(ProductSku.product_id == p.id, ProductSku.enabled == True)  # noqa: E712
        ).scalars()
    )
    po = ProductOut.model_validate(p)
    po.skus = [ProductSkuOut.model_validate(s) for s in skus]
    return Resp(data=po)


@router.get("/{pid}/mockup")
def get_product_mockup(
    pid: int,
    color: str = "#ffffff",
    side: str = "front",
    db: Session = Depends(get_db),
) -> Response:
    """商品底图（SVG），按当前颜色 / 正反面实时生成。

    C 端编辑器底图统一从这里取，避免各端写死。颜色支持英文名 / 中文名 / hex。
    """
    p = db.get(Product, pid)
    slug = None
    if p and p.category_id:
        cat = db.get(ProductCategory, p.category_id)
        slug = cat.slug if cat else None
    svg = product_mockup(slug, color=color, side=side)
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "public, max-age=300"},
    )


@router.get("/sku/{sku_id}", response_model=Resp[ProductSkuOut])
def get_sku(sku_id: int, db: Session = Depends(get_db)) -> Resp[ProductSkuOut]:
    sku = db.get(ProductSku, sku_id)
    if not sku or not sku.enabled:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="sku not found")
    return Resp(data=ProductSkuOut.model_validate(sku))
