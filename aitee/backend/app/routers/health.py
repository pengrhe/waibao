from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.schemas.common import HealthInfo, Resp

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Resp[HealthInfo])
def health(db: Session = Depends(get_db)) -> Resp[HealthInfo]:
    try:
        db.execute(text("select 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"

    info = HealthInfo(
        status="ok",
        name=settings.APP_NAME,
        env=settings.APP_ENV,
        db=db_status,
    )
    return Resp(data=info)
