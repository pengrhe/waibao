from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import hash_password
from app.deps.auth import require_role
from app.models import Partner
from app.schemas.admin import PartnerIn
from app.schemas.common import Resp

router = APIRouter(prefix="/admin/partners", tags=["admin-partners"])


def _to_dict(p: Partner) -> dict:
    return {
        "id": p.id,
        "username": p.username,
        "name": p.name,
        "phone": p.phone,
        "channel": p.channel,
        "profit_ratio": float(p.profit_ratio),
        "bank_card": p.bank_card,
        "bank_name": p.bank_name,
        "balance": float(p.balance or 0),
        "total_earned": float(p.total_earned or 0),
        "total_withdrew": float(p.total_withdrew or 0),
        "status": p.status,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


@router.get("", response_model=Resp[dict])
def list_partners(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    status_filter: str = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(Partner).order_by(Partner.id.desc())
    if keyword:
        stmt = stmt.where(or_(Partner.username.ilike(f"%{keyword}%"), Partner.name.ilike(f"%{keyword}%")))
    if status_filter:
        stmt = stmt.where(Partner.status == status_filter)
    all_items = db.execute(stmt).scalars().all()
    total = len(all_items)
    start = (page - 1) * page_size
    items = all_items[start:start + page_size]
    return Resp(data={"items": [_to_dict(p) for p in items], "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=Resp[dict])
def create_partner(
    payload: PartnerIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    data = payload.model_dump()
    pw = data.pop("password", None) or "partner123"
    p = Partner(**data, password_hash=hash_password(pw))
    db.add(p)
    db.commit()
    db.refresh(p)
    return Resp(data=_to_dict(p))


@router.put("/{pid}", response_model=Resp[dict])
def update_partner(
    pid: int,
    payload: PartnerIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    p = db.get(Partner, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    data = payload.model_dump(exclude_none=True)
    pw = data.pop("password", None)
    for k, v in data.items():
        setattr(p, k, v)
    if pw:
        p.password_hash = hash_password(pw)
    db.commit()
    return Resp(data=_to_dict(p))


@router.delete("/{pid}", response_model=Resp[dict])
def delete_partner(
    pid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    p = db.get(Partner, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(p)
    db.commit()
    return Resp(data={"deleted": pid})


@router.post("/{pid}/audit", response_model=Resp[dict])
def audit_partner(
    pid: int,
    action: str,
    reject_reason: str = "",
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    """action = approve / reject"""
    p = db.get(Partner, pid)
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    if action == "approve":
        p.status = "active"
        p.reject_reason = None
    elif action == "reject":
        p.status = "rejected"
        p.reject_reason = reject_reason or "审核不通过"
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="action must be approve|reject")
    db.commit()
    return Resp(data={"id": pid, "status": p.status})
