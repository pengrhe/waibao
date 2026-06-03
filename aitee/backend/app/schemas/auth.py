from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class LoginIn(BaseModel):
    username: str
    password: str


class BUserOut(BaseModel):
    id: int
    username: str
    name: Optional[str] = None
    role: str
    extra: Optional[dict] = None


class LoginOut(BaseModel):
    token: str
    user: BUserOut
