from __future__ import annotations
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import Design, User
from app.schemas.c import DesignIn, DesignOut
from app.schemas.common import Resp

router = APIRouter(prefix="/designs", tags=["c-design"])


@router.get("", response_model=Resp[List[DesignOut]])
def list_designs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[DesignOut]]:
    items = db.execute(
        select(Design).where(Design.user_id == user.id).order_by(Design.id.desc())
    ).scalars().all()
    return Resp(data=[DesignOut.model_validate(d) for d in items])


@router.post("", response_model=Resp[DesignOut])
def create_design(
    payload: DesignIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[DesignOut]:
    d = Design(user_id=user.id, status="saved", **payload.model_dump())
    db.add(d)
    db.commit()
    db.refresh(d)
    return Resp(data=DesignOut.model_validate(d))


@router.get("/{did}", response_model=Resp[DesignOut])
def get_design(
    did: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[DesignOut]:
    d = db.get(Design, did)
    if not d or d.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="design not found")
    return Resp(data=DesignOut.model_validate(d))


@router.put("/{did}", response_model=Resp[DesignOut])
def update_design(
    did: int,
    payload: DesignIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[DesignOut]:
    d = db.get(Design, did)
    if not d or d.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="design not found")
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(d, k, v)
    d.status = "saved"
    db.commit()
    db.refresh(d)
    return Resp(data=DesignOut.model_validate(d))


@router.delete("/{did}", response_model=Resp[dict])
def delete_design(
    did: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[dict]:
    d = db.get(Design, did)
    if not d or d.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="design not found")
    db.delete(d)
    db.commit()
    return Resp(data={"deleted": did})
