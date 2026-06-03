from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import get_b_payload
from app.schemas.auth import LoginIn, LoginOut, BUserOut
from app.schemas.common import Resp
from app.services.b_auth import authenticate

router = APIRouter(prefix="/admin/auth", tags=["admin-auth"])


@router.post("/login", response_model=Resp[LoginOut])
def admin_login(payload: LoginIn, db: Session = Depends(get_db)) -> Resp[LoginOut]:
    token, user_info = authenticate(db, role="admin", username=payload.username, password=payload.password)
    db.commit()
    return Resp(data=LoginOut(token=token, user=BUserOut(**user_info)))


@router.get("/me", response_model=Resp[dict])
def me(payload: dict = Depends(get_b_payload)) -> Resp[dict]:
    return Resp(data=payload)
