from __future__ import annotations
from typing import Dict, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import CityIp, CityIpItem, CulturalElement
from app.schemas.c import CityIpItemOut, CityIpOut
from app.schemas.common import Resp

router = APIRouter(prefix="/city-ip", tags=["c-city-ip"])

POPULAR = ["北京", "上海", "深圳", "成都", "广州", "杭州", "西安", "厦门", "重庆", "南京"]


@router.get("/popular", response_model=Resp[List[str]])
def popular() -> Resp[List[str]]:
    return Resp(data=POPULAR)


@router.get("/hints", response_model=Resp[dict])
def hints(db: Session = Depends(get_db)) -> Resp[dict]:
    """每个城市的 1 句话提示语。"""
    items = db.execute(select(CulturalElement)).scalars().all()
    by_city: Dict[str, List[str]] = {}
    for e in items:
        by_city.setdefault(e.city, []).append(e.name)
    out = {city: f"代表元素：{', '.join(names[:4])}" for city, names in by_city.items()}
    return Resp(data=out)


def _to_out(db: Session, ip: CityIp) -> CityIpOut:
    items = db.execute(
        select(CityIpItem).where(CityIpItem.city_ip_id == ip.id).order_by(CityIpItem.sort, CityIpItem.id)
    ).scalars().all()
    elements = db.execute(
        select(CulturalElement).where(CulturalElement.city == ip.city, CulturalElement.enabled == True)  # noqa: E712
    ).scalars().all()
    out = CityIpOut.model_validate(ip)
    out.items = [CityIpItemOut.model_validate(i) for i in items]
    out.elements = [e.name for e in elements]
    out.total_count = len(items)
    return out


@router.get("/{city}", response_model=Resp[CityIpOut])
def get_city_ip(city: str, db: Session = Depends(get_db)) -> Resp[CityIpOut]:
    ip = db.execute(select(CityIp).where(CityIp.city == city)).scalar_one_or_none()
    if not ip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="city ip not found, 请先生成")
    return Resp(data=_to_out(db, ip))


class RegenIn(BaseModel):
    elements: List[str] = []


@router.post("/{city}/regenerate", response_model=Resp[CityIpOut])
def regenerate_city(
    city: str,
    payload: RegenIn,
    db: Session = Depends(get_db),
) -> Resp[CityIpOut]:
    """重新生成：M2 简化版直接打乱顺序 + bump updated_at；真实 AI 调用在 routers/c/ai.py 的 city_ip 接口里。"""
    ip = db.execute(select(CityIp).where(CityIp.city == city)).scalar_one_or_none()
    if not ip:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="city ip not found")
    items = db.execute(
        select(CityIpItem).where(CityIpItem.city_ip_id == ip.id)
    ).scalars().all()
    import random
    random.shuffle(items)
    for idx, it in enumerate(items):
        it.sort = idx
    db.commit()
    return Resp(data=_to_out(db, ip))
