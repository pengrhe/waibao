from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Pattern, PatternCategory
from app.schemas.c import PatternCategoryOut, PatternOut
from app.schemas.common import Resp

router = APIRouter(prefix="/patterns", tags=["c-pattern"])


@router.get("/categories", response_model=Resp[List[PatternCategoryOut]])
def list_categories(db: Session = Depends(get_db)) -> Resp[List[PatternCategoryOut]]:
    items = db.execute(
        select(PatternCategory).order_by(PatternCategory.sort, PatternCategory.id)
    ).scalars().all()
    return Resp(data=[PatternCategoryOut.model_validate(c) for c in items])


@router.get("", response_model=Resp[List[PatternOut]])
def list_patterns(
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Resp[List[PatternOut]]:
    stmt = select(Pattern).where(Pattern.enabled == True).order_by(Pattern.sort, Pattern.id)  # noqa: E712
    if category_id:
        stmt = stmt.where(Pattern.category_id == category_id)
    items = db.execute(stmt).scalars().all()
    if tag:
        items = [p for p in items if p.tags and tag in p.tags]
    return Resp(data=[PatternOut.model_validate(p) for p in items])


@router.get("/{pid}", response_model=Resp[PatternOut])
def get_pattern(pid: int, db: Session = Depends(get_db)) -> Resp[PatternOut]:
    p = db.get(Pattern, pid)
    if not p:
        from fastapi import HTTPException, status
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="pattern not found")
    return Resp(data=PatternOut.model_validate(p))
