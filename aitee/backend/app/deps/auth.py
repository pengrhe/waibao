from __future__ import annotations

from typing import Literal

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_token


def _extract_token(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing token")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token header")
    return parts[1]


def get_c_payload(authorization: str | None = Header(default=None)) -> dict:
    token = _extract_token(authorization)
    try:
        return decode_token(token, "c")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def get_b_payload(authorization: str | None = Header(default=None)) -> dict:
    token = _extract_token(authorization)
    try:
        return decode_token(token, "b")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


def require_role(*roles: str):
    def _dep(payload: dict = Depends(get_b_payload)) -> dict:
        role = payload.get("role")
        if roles and role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
        return payload

    return _dep
