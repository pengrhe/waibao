"""C 端用户管理（搜索 + 禁用）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import require_role
from app.models import User
from app.schemas.admin import CUserIn
from app.schemas.common import Resp

router = APIRouter(prefix="/admin/users", tags=["admin-users"])


def _to_dict(u: User) -> dict:
    return {
        "id": u.id,
        "phone": u.phone,
        "nickname": u.nickname,
        "avatar_url": u.avatar_url,
        "city": u.city,
        "status": u.status,
        "tags": u.tags,
        "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        "created_at": u.created_at.isoformat() if u.created_at else None,
    }


@router.get("", response_model=Resp[dict])
def list_users(
    page: int = 1,
    page_size: int = 20,
    keyword: str = None,
    status_filter: str = None,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    stmt = select(User).order_by(User.id.desc())
    if keyword:
        stmt = stmt.where(or_(User.phone.ilike(f"%{keyword}%"), User.nickname.ilike(f"%{keyword}%")))
    if status_filter:
        stmt = stmt.where(User.status == status_filter)
    all_items = db.execute(stmt).scalars().all()
    total = len(all_items)
    start = (page - 1) * page_size
    items = all_items[start:start + page_size]
    return Resp(data={"items": [_to_dict(u) for u in items], "total": total, "page": page, "page_size": page_size})


@router.put("/{uid}", response_model=Resp[dict])
def update_user(
    uid: int,
    payload: CUserIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    u = db.get(User, uid)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(u, k, v)
    db.commit()
    return Resp(data=_to_dict(u))


@router.post("/{uid}/disable", response_model=Resp[dict])
def disable_user(
    uid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    u = db.get(User, uid)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    u.status = "disabled"
    db.commit()
    return Resp(data={"id": uid, "status": "disabled"})


@router.post("/{uid}/enable", response_model=Resp[dict])
def enable_user(
    uid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    u = db.get(User, uid)
    if not u:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    u.status = "active"
    db.commit()
    return Resp(data={"id": uid, "status": "active"})
