from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import hash_password
from app.deps.auth import require_role
from app.models import Store, StoreStaff
from app.schemas.admin import StoreIn
from app.schemas.common import Resp

router = APIRouter(prefix="/admin/stores", tags=["admin-stores"])


def _to_dict(s: Store) -> dict:
    return {
        "id": s.id,
        "username": s.username,
        "name": s.name,
        "owner": s.owner,
        "phone": s.phone,
        "province": s.province,
        "city": s.city,
        "district": s.district,
        "address": s.address,
        "management_fee_ratio": float(s.management_fee_ratio),
        "settle_mode": s.settle_mode,
        "bank_card": s.bank_card,
        "bank_name": s.bank_name,
        "balance": float(s.balance or 0),
        "promotion": s.promotion,
        "status": s.status,
    }


@router.get("", response_model=Resp[dict])
def list_stores(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    status_filter: str = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(Store).order_by(Store.id.desc())
    if keyword:
        stmt = stmt.where(or_(Store.username.ilike(f"%{keyword}%"), Store.name.ilike(f"%{keyword}%"), Store.city.ilike(f"%{keyword}%")))
    if status_filter:
        stmt = stmt.where(Store.status == status_filter)
    all_items = db.execute(stmt).scalars().all()
    total = len(all_items)
    start = (page - 1) * page_size
    items = all_items[start:start + page_size]
    return Resp(data={"items": [_to_dict(s) for s in items], "total": total, "page": page, "page_size": page_size})


@router.post("", response_model=Resp[dict])
def create_store(
    payload: StoreIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    data = payload.model_dump()
    pw = data.pop("password", None) or "store123"
    s = Store(**data, password_hash=hash_password(pw))
    db.add(s)
    db.commit()
    db.refresh(s)
    return Resp(data=_to_dict(s))


@router.put("/{sid}", response_model=Resp[dict])
def update_store(
    sid: int,
    payload: StoreIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    s = db.get(Store, sid)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    data = payload.model_dump(exclude_none=True)
    pw = data.pop("password", None)
    for k, v in data.items():
        setattr(s, k, v)
    if pw:
        s.password_hash = hash_password(pw)
    db.commit()
    return Resp(data=_to_dict(s))


@router.delete("/{sid}", response_model=Resp[dict])
def delete_store(
    sid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    s = db.get(Store, sid)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(s)
    db.commit()
    return Resp(data={"deleted": sid})


@router.post("/{sid}/audit", response_model=Resp[dict])
def audit_store(
    sid: int,
    action: str,
    reject_reason: str = "",
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    s = db.get(Store, sid)
    if not s:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    if action == "approve":
        s.status = "active"
        s.reject_reason = None
    elif action == "reject":
        s.status = "rejected"
        s.reject_reason = reject_reason or "审核不通过"
    else:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="action must be approve|reject")
    db.commit()
    return Resp(data={"id": sid, "status": s.status})


@router.get("/{sid}/staffs", response_model=Resp[dict])
def list_staffs(
    sid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    items = db.execute(select(StoreStaff).where(StoreStaff.store_id == sid)).scalars().all()
    return Resp(data={"items": [
        {"id": st.id, "username": st.username, "name": st.name, "role": st.role, "enabled": st.enabled}
        for st in items
    ], "total": len(items)})
