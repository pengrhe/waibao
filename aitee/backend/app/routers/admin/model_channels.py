"""模型通道：CRUD + 切换 active（同一时刻仅一个 is_active=True）。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import require_role
from app.models import ModelChannel
from app.schemas.admin import ModelChannelIn
from app.schemas.common import Resp

router = APIRouter(prefix="/admin/model-channels", tags=["admin-model-channels"])


def _to_dict(m: ModelChannel) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "provider": m.provider,
        "base_url": m.base_url,
        "api_key": (m.api_key[:6] + "..." + m.api_key[-4:]) if m.api_key else "",
        "model_name": m.model_name,
        "enabled": m.enabled,
        "is_active": m.is_active,
        "extra": m.extra,
        "remark": m.remark,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "updated_at": m.updated_at.isoformat() if m.updated_at else None,
    }


@router.get("", response_model=Resp[dict])
def list_channels(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    items = db.execute(select(ModelChannel).order_by(ModelChannel.id.desc())).scalars().all()
    return Resp(data={"items": [_to_dict(m) for m in items], "total": len(items)})


@router.get("/{cid}", response_model=Resp[dict])
def get_channel(cid: int, db: Session = Depends(get_db), _=Depends(require_role("admin"))) -> Resp[dict]:
    m = db.get(ModelChannel, cid)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    return Resp(data=_to_dict(m))


@router.post("", response_model=Resp[dict])
def create_channel(
    payload: ModelChannelIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    if payload.is_active:
        for other in db.execute(select(ModelChannel).where(ModelChannel.is_active == True)).scalars():  # noqa: E712
            other.is_active = False
    m = ModelChannel(**payload.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return Resp(data=_to_dict(m))


@router.put("/{cid}", response_model=Resp[dict])
def update_channel(
    cid: int,
    payload: ModelChannelIn,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    m = db.get(ModelChannel, cid)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    data = payload.model_dump()
    # 若 api_key 为空或 mask 形式，不覆盖
    if not data.get("api_key") or "..." in data.get("api_key", ""):
        data.pop("api_key", None)
    if data.get("is_active"):
        for other in db.execute(select(ModelChannel).where(ModelChannel.is_active == True, ModelChannel.id != cid)).scalars():  # noqa: E712
            other.is_active = False
    for k, v in data.items():
        setattr(m, k, v)
    db.commit()
    db.refresh(m)
    return Resp(data=_to_dict(m))


@router.delete("/{cid}", response_model=Resp[dict])
def delete_channel(
    cid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    m = db.get(ModelChannel, cid)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(m)
    db.commit()
    return Resp(data={"deleted": cid})


@router.post("/{cid}/activate", response_model=Resp[dict])
def activate(
    cid: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin")),
) -> Resp[dict]:
    m = db.get(ModelChannel, cid)
    if not m:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
    for other in db.execute(select(ModelChannel).where(ModelChannel.is_active == True, ModelChannel.id != cid)).scalars():  # noqa: E712
        other.is_active = False
    m.is_active = True
    m.enabled = True
    db.commit()
    return Resp(data={"id": cid, "is_active": True})
