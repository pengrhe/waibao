from __future__ import annotations
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import Address, User
from app.schemas.c import AddressIn, AddressOut
from app.schemas.common import Resp

router = APIRouter(prefix="/addresses", tags=["c-address"])


def _list_user(db: Session, user_id: int) -> List[Address]:
    return list(
        db.execute(
            select(Address).where(Address.user_id == user_id).order_by(Address.is_default.desc(), Address.id.desc())
        ).scalars()
    )


@router.get("", response_model=Resp[List[AddressOut]])
def list_addresses(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[AddressOut]]:
    return Resp(data=[AddressOut.model_validate(a) for a in _list_user(db, user.id)])


@router.post("", response_model=Resp[AddressOut])
def create_address(
    payload: AddressIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[AddressOut]:
    if payload.is_default:
        for a in _list_user(db, user.id):
            a.is_default = False
    a = Address(user_id=user.id, **payload.model_dump())
    db.add(a)
    db.flush()
    # 第一条地址自动设默认
    if len(_list_user(db, user.id)) == 1:
        a.is_default = True
    db.commit()
    db.refresh(a)
    return Resp(data=AddressOut.model_validate(a))


@router.put("/{aid}", response_model=Resp[AddressOut])
def update_address(
    aid: int,
    payload: AddressIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[AddressOut]:
    a = db.get(Address, aid)
    if not a or a.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="address not found")
    if payload.is_default:
        for other in _list_user(db, user.id):
            if other.id != aid:
                other.is_default = False
    for k, v in payload.model_dump().items():
        setattr(a, k, v)
    db.commit()
    db.refresh(a)
    return Resp(data=AddressOut.model_validate(a))


@router.delete("/{aid}", response_model=Resp[List[AddressOut]])
def delete_address(
    aid: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[List[AddressOut]]:
    a = db.get(Address, aid)
    if not a or a.user_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="address not found")
    db.delete(a)
    db.flush()
    remaining = _list_user(db, user.id)
    if remaining and not any(x.is_default for x in remaining):
        remaining[0].is_default = True
    db.commit()
    return Resp(data=[AddressOut.model_validate(x) for x in _list_user(db, user.id)])


@router.get("/default", response_model=Resp[Optional[AddressOut]])
def get_default(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[Optional[AddressOut]]:
    addrs = _list_user(db, user.id)
    if not addrs:
        return Resp(data=None)
    default = next((a for a in addrs if a.is_default), addrs[0])
    return Resp(data=AddressOut.model_validate(default))
