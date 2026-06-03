from __future__ import annotations

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Resp(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "ok"
    data: Optional[T] = None


class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 20


class HealthInfo(BaseModel):
    status: str
    name: str
    env: str
    db: str
    version: str = "0.1.0"
    extras: Dict[str, Any] = {}
