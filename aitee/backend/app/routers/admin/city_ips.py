"""城市 IP / 城市 IP 子项 / 文化元素 三套 CRUD。"""
from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import require_role
from app.models import CityIp, CityIpItem, CulturalElement
from app.schemas.admin import CityIpIn, CulturalElementIn
from app.schemas.common import Resp

router = APIRouter(prefix="/admin/city-ips", tags=["admin-city-ips"])
items_router = APIRouter(prefix="/admin/city-ip-items", tags=["admin-city-ip-items"])
elements_router = APIRouter(prefix="/admin/cultural-elements", tags=["admin-cultural-elements"])


def _ip_dict(c: CityIp, items: list, elements: list) -> dict:
    return {
        "id": c.id,
        "city": c.city,
        "description": c.description,
        "cover_url": c.cover_url,
        "created_at": c.created_at.isoformat() if c.created_at else None,
        "items": [{"id": i.id, "category": i.category, "title": i.title, "image_url": i.image_url, "sort": i.sort, "source": i.source} for i in items],
        "elements": [{"id": e.id, "name": e.name, "category": e.category, "description": e.description, "style_hint": e.style_hint, "enabled": e.enabled} for e in elements],
    }


@router.get("", response_model=Resp[dict])
def list_city_ips(
    keyword: str = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(CityIp).order_by(CityIp.id)
    if keyword:
        stmt = stmt.where(CityIp.city.ilike(f"%{keyword}%"))
    items = db.execute(stmt).scalars().all()
    out = []
    for c in items:
        sub_items = list(db.execute(select(CityIpItem).where(CityIpItem.city_ip_id == c.id).order_by(CityIpItem.sort)).scalars())
        elems = list(db.execute(select(CulturalElement).where(CulturalElement.city == c.city).order_by(CulturalElement.sort)).scalars())
        out.append(_ip_dict(c, sub_items, elems))
    return Resp(data={"items": out, "total": len(out)})


@router.post("", response_model=Resp[dict])
def create_city_ip(
    payload: CityIpIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    if db.execute(select(CityIp).where(CityIp.city == payload.city)).scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="city already exists")
    c = CityIp(**payload.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return Resp(data=_ip_dict(c, [], []))


@router.put("/{cid}", response_model=Resp[dict])
def update_city_ip(
    cid: int,
    payload: CityIpIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    c = db.get(CityIp, cid)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    for k, v in payload.model_dump().items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return Resp(data={"id": cid, "city": c.city})


@router.delete("/{cid}", response_model=Resp[dict])
def delete_city_ip(
    cid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    c = db.get(CityIp, cid)
    if not c:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(c)
    db.commit()
    return Resp(data={"deleted": cid})


# ============ items ============

class CityIpItemIn(BaseModel):
    city_ip_id: int
    category: str
    title: str
    image_url: str
    source: str = "builtin"
    sort: int = 0


@items_router.post("", response_model=Resp[dict])
def create_item(
    payload: CityIpItemIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    it = CityIpItem(**payload.model_dump())
    db.add(it)
    db.commit()
    db.refresh(it)
    return Resp(data={"id": it.id})


@items_router.delete("/{iid}", response_model=Resp[dict])
def delete_item(
    iid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    it = db.get(CityIpItem, iid)
    if not it:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(it)
    db.commit()
    return Resp(data={"deleted": iid})


# ============ elements ============

@elements_router.get("", response_model=Resp[dict])
def list_elements(
    city: str = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(CulturalElement).order_by(CulturalElement.city, CulturalElement.sort)
    if city:
        stmt = stmt.where(CulturalElement.city == city)
    items = db.execute(stmt).scalars().all()
    return Resp(data={"items": [
        {"id": e.id, "city": e.city, "name": e.name, "category": e.category, "description": e.description, "style_hint": e.style_hint, "enabled": e.enabled, "sort": e.sort}
        for e in items
    ], "total": len(items)})


@elements_router.post("", response_model=Resp[dict])
def create_element(
    payload: CulturalElementIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    e = CulturalElement(**payload.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return Resp(data={"id": e.id})


@elements_router.put("/{eid}", response_model=Resp[dict])
def update_element(
    eid: int,
    payload: CulturalElementIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    e = db.get(CulturalElement, eid)
    if not e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    for k, v in payload.model_dump().items():
        setattr(e, k, v)
    db.commit()
    return Resp(data={"id": eid})


@elements_router.delete("/{eid}", response_model=Resp[dict])
def delete_element(
    eid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    e = db.get(CulturalElement, eid)
    if not e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(e)
    db.commit()
    return Resp(data={"deleted": eid})
