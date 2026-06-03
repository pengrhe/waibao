"""B 端登录公共逻辑：admin / partner / store / staff 共用一套验证 + token 签发。"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Literal, Tuple, Type

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models import AdminUser, Partner, Store, StoreStaff

BRole = Literal["admin", "partner", "store", "staff"]

_MODEL_MAP: Dict[str, Type] = {
    "admin": AdminUser,
    "partner": Partner,
    "store": Store,
    "staff": StoreStaff,
}


def authenticate(
    db: Session,
    *,
    role: BRole,
    username: str,
    password: str,
) -> Tuple[str, dict]:
    Model = _MODEL_MAP[role]
    user = db.execute(select(Model).where(Model.username == username)).scalar_one_or_none()
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    if hasattr(user, "enabled") and not getattr(user, "enabled"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="账号已停用")
    if hasattr(user, "status") and getattr(user, "status") not in ("active", None):
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail=f"账号状态：{user.status}")
    if not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")

    extra = {"role": role}
    if role == "staff":
        extra["store_id"] = user.store_id
    if role == "admin" and getattr(user, "role", None):
        extra["admin_role"] = user.role

    token = create_access_token(subject=str(user.id), realm="b", extra=extra)

    user.last_login_at = datetime.now(timezone.utc)
    db.flush()

    info = {
        "id": user.id,
        "username": user.username,
        "name": getattr(user, "name", None),
        "role": role,
        "extra": {k: v for k, v in extra.items() if k != "role"},
    }
    return token, info
