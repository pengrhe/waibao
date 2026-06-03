"""伙伴端 / 加盟店端 / 店员端 三个 B 端 H5 共用的登录入口。"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import get_b_payload
from app.schemas.auth import LoginIn, LoginOut, BUserOut
from app.schemas.common import Resp
from app.services.b_auth import authenticate

partner_router = APIRouter(prefix="/partner/auth", tags=["partner-auth"])
store_router = APIRouter(prefix="/store/auth", tags=["store-auth"])
staff_router = APIRouter(prefix="/staff/auth", tags=["staff-auth"])


def _make_login(role: str):
    def _login(payload: LoginIn, db: Session = Depends(get_db)) -> Resp[LoginOut]:
        token, user_info = authenticate(db, role=role, username=payload.username, password=payload.password)
        db.commit()
        return Resp(data=LoginOut(token=token, user=BUserOut(**user_info)))

    return _login


def _make_me():
    def _me(payload: dict = Depends(get_b_payload)) -> Resp[dict]:
        return Resp(data=payload)

    return _me


partner_router.add_api_route("/login", _make_login("partner"), methods=["POST"], response_model=Resp[LoginOut])
partner_router.add_api_route("/me", _make_me(), methods=["GET"], response_model=Resp[dict])

store_router.add_api_route("/login", _make_login("store"), methods=["POST"], response_model=Resp[LoginOut])
store_router.add_api_route("/me", _make_me(), methods=["GET"], response_model=Resp[dict])

staff_router.add_api_route("/login", _make_login("staff"), methods=["POST"], response_model=Resp[LoginOut])
staff_router.add_api_route("/me", _make_me(), methods=["GET"], response_model=Resp[dict])
