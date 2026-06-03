from __future__ import annotations
from typing import List

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import PushMessage, User
from app.schemas.common import Resp

router = APIRouter(prefix="/messages", tags=["c-message"])


@router.get("", response_model=Resp[List[dict]])
def list_messages(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[dict]]:
    items = db.execute(
        select(PushMessage)
        .where(PushMessage.user_type == "c_user", PushMessage.user_id == user.id)
        .order_by(PushMessage.id.desc())
    ).scalars().all()
    return Resp(data=[
        {
            "id": m.id,
            "title": m.title,
            "body": m.body,
            "channel": m.channel,
            "template": m.template,
            "link_to": m.link_to,
            "payload": m.payload,
            "status": m.status,
            "sent_at": m.sent_at.isoformat() if m.sent_at else None,
            "read_at": m.read_at.isoformat() if m.read_at else None,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        }
        for m in items
    ])


@router.get("/unread-count", response_model=Resp[dict])
def unread_count(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[dict]:
    items = db.execute(
        select(PushMessage).where(
            PushMessage.user_type == "c_user",
            PushMessage.user_id == user.id,
            PushMessage.read_at.is_(None),
        )
    ).scalars().all()
    return Resp(data={"count": len(items)})


@router.post("/{mid}/read", response_model=Resp[dict])
def mark_read(
    mid: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[dict]:
    m = db.get(PushMessage, mid)
    if not m or m.user_type != "c_user" or m.user_id != user.id:
        return Resp(code=404, msg="not found", data={"ok": False})
    if not m.read_at:
        m.read_at = datetime.now(timezone.utc)
        m.status = "read"
        db.commit()
    return Resp(data={"ok": True})


@router.post("/read-all", response_model=Resp[dict])
def mark_all_read(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[dict]:
    now = datetime.now(timezone.utc)
    items = db.execute(
        select(PushMessage).where(
            PushMessage.user_type == "c_user",
            PushMessage.user_id == user.id,
            PushMessage.read_at.is_(None),
        )
    ).scalars().all()
    for m in items:
        m.read_at = now
        m.status = "read"
    db.commit()
    return Resp(data={"count": len(items)})
