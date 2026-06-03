"""二维码管理：生成三类二维码（伙伴推广 / 门店下单 / 店员核销）。"""
from __future__ import annotations

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import get_db
from app.deps.auth import require_role
from app.models import Partner, QrCode, Store, StoreStaff
from app.schemas.admin import QrCodeIn
from app.schemas.common import Resp

router = APIRouter(prefix="/admin/qrcodes", tags=["admin-qrcodes"])


def _to_dict(q: QrCode) -> dict:
    return {
        "id": q.id,
        "type": q.type,
        "code": q.code,
        "owner_type": q.owner_type,
        "owner_id": q.owner_id,
        "target_url": q.target_url,
        "image_url": q.image_url,
        "style": q.style,
        "enabled": q.enabled,
        "scan_count": q.scan_count,
        "created_at": q.created_at.isoformat() if q.created_at else None,
    }


def _gen_code(type_: str) -> str:
    return f"{type_[:3]}_{secrets.token_urlsafe(8)}"


@router.get("", response_model=Resp[dict])
def list_qr(
    type_: str = None,
    owner_type: str = None,
    owner_id: int = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(QrCode).order_by(QrCode.id.desc())
    if type_:
        stmt = stmt.where(QrCode.type == type_)
    if owner_type:
        stmt = stmt.where(QrCode.owner_type == owner_type)
    if owner_id:
        stmt = stmt.where(QrCode.owner_id == owner_id)
    items = db.execute(stmt).scalars().all()
    return Resp(data={"items": [_to_dict(q) for q in items], "total": len(items)})


@router.post("", response_model=Resp[dict])
def create_qr(
    payload: QrCodeIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    code = payload.code or _gen_code(payload.type)
    if db.execute(select(QrCode).where(QrCode.code == code)).scalar_one_or_none():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="code already exists")
    # 校验 owner 存在
    if payload.owner_type == "partner" and payload.owner_id:
        if not db.get(Partner, payload.owner_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="partner not found")
    elif payload.owner_type == "store" and payload.owner_id:
        if not db.get(Store, payload.owner_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="store not found")
    elif payload.owner_type == "staff" and payload.owner_id:
        if not db.get(StoreStaff, payload.owner_id):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="staff not found")

    target = payload.target_url
    if not target.startswith("http"):
        target = settings.PUBLIC_BASE_URL.rstrip("/") + "/" + target.lstrip("/")
    q = QrCode(
        type=payload.type,
        code=code,
        owner_type=payload.owner_type,
        owner_id=payload.owner_id,
        target_url=target,
        style=payload.style,
        enabled=payload.enabled,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return Resp(data=_to_dict(q))


@router.delete("/{qid}", response_model=Resp[dict])
def delete_qr(
    qid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    q = db.get(QrCode, qid)
    if not q:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(q)
    db.commit()
    return Resp(data={"deleted": qid})


@router.post("/{qid}/toggle", response_model=Resp[dict])
def toggle_qr(
    qid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    q = db.get(QrCode, qid)
    if not q:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    q.enabled = not bool(q.enabled)
    db.commit()
    return Resp(data={"id": qid, "enabled": q.enabled})
