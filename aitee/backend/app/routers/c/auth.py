from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_current_user
from app.models import User
from app.schemas.c import CLoginIn, CLoginOut, UserProfile
from app.schemas.common import Resp
from app.services.c_auth import mock_login

router = APIRouter(prefix="/user/auth", tags=["c-auth"])


@router.post("/login", response_model=Resp[CLoginOut])
def login(payload: CLoginIn, db: Session = Depends(get_db)) -> Resp[CLoginOut]:
    token, user = mock_login(
        db,
        channel=payload.channel,
        phone=payload.phone,
        nickname=payload.nickname,
    )
    db.commit()
    return Resp(data=CLoginOut(token=token, user=UserProfile.model_validate(user)))


@router.get("/me", response_model=Resp[UserProfile])
def me(user: User = Depends(get_current_user)) -> Resp[UserProfile]:
    return Resp(data=UserProfile.model_validate(user))
