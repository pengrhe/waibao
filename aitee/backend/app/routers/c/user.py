from __future__ import annotations
from typing import Dict, List

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import User, UserPref
from app.schemas.c import UserProfile
from app.schemas.common import Resp

router = APIRouter(prefix="/user", tags=["c-user"])


class ProfileUpdateIn(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    city: str | None = None


@router.get("/profile", response_model=Resp[UserProfile])
def get_profile(user: User = Depends(get_current_user)) -> Resp[UserProfile]:
    return Resp(data=UserProfile.model_validate(user))


@router.put("/profile", response_model=Resp[UserProfile])
def update_profile(
    payload: ProfileUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[UserProfile]:
    for k, v in payload.model_dump(exclude_none=True).items():
        setattr(user, k, v)
    db.commit()
    db.refresh(user)
    return Resp(data=UserProfile.model_validate(user))


class PrefIn(BaseModel):
    pref_type: str  # style/product/color/size ...
    value: str


@router.post("/prefs", response_model=Resp[dict])
def record_pref(
    payload: PrefIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[dict]:
    """偏好上报：累计 count，连续 3 次同值标 default。"""
    pref = db.execute(
        select(UserPref).where(
            UserPref.user_id == user.id,
            UserPref.pref_type == payload.pref_type,
            UserPref.value == payload.value,
        )
    ).scalar_one_or_none()

    if not pref:
        pref = UserPref(
            user_id=user.id,
            pref_type=payload.pref_type,
            value=payload.value,
            count=1,
        )
        db.add(pref)
    else:
        pref.count += 1

    # 连续 3 次同值 → 标 default，其他同 pref_type 取消 default
    if pref.count >= 3:
        db.flush()
        for other in db.execute(
            select(UserPref).where(
                UserPref.user_id == user.id,
                UserPref.pref_type == payload.pref_type,
                UserPref.id != pref.id,
            )
        ).scalars():
            other.is_default = False
        pref.is_default = True

    db.commit()
    return Resp(data={"pref_type": payload.pref_type, "value": payload.value, "count": pref.count, "is_default": pref.is_default})


@router.get("/prefs", response_model=Resp[dict])
def list_prefs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Resp[dict]:
    """返回每个 pref_type 的当前默认值 + 全部历史。"""
    items = db.execute(
        select(UserPref).where(UserPref.user_id == user.id).order_by(UserPref.count.desc())
    ).scalars().all()

    defaults: Dict[str, str] = {}
    history: List[dict] = []
    for p in items:
        history.append({
            "pref_type": p.pref_type,
            "value": p.value,
            "count": p.count,
            "is_default": p.is_default,
        })
        if p.is_default and p.pref_type not in defaults:
            defaults[p.pref_type] = p.value
    return Resp(data={"defaults": defaults, "history": history})
