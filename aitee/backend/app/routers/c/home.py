from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Banner, Topic
from app.schemas.c import BannerOut, TopicOut
from app.schemas.common import Resp

router = APIRouter(prefix="/home", tags=["c-home"])


@router.get("/banners", response_model=Resp[List[BannerOut]])
def banners(position: str = "home_top", db: Session = Depends(get_db)) -> Resp[List[BannerOut]]:
    items = db.execute(
        select(Banner).where(Banner.position == position, Banner.enabled == True).order_by(Banner.sort, Banner.id)  # noqa: E712
    ).scalars().all()
    return Resp(data=[BannerOut.model_validate(b) for b in items])


@router.get("/topics", response_model=Resp[List[TopicOut]])
def topics(db: Session = Depends(get_db)) -> Resp[List[TopicOut]]:
    items = db.execute(
        select(Topic).where(Topic.enabled == True).order_by(Topic.sort, Topic.id)  # noqa: E712
    ).scalars().all()
    return Resp(data=[TopicOut.model_validate(t) for t in items])
