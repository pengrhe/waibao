"""Admin 通用 CRUD 工厂：列表（分页+模糊搜索）/ 详情 / 创建 / 更新 / 删除 / 启停。

每个 admin 域只需提供：model、schema_in、keyword_columns，即可生成一组 router。
"""
from __future__ import annotations

from typing import Any, Callable, List, Optional, Sequence, Type

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.auth import require_role
from app.schemas.common import Resp


def build_crud(
    *,
    name: str,
    model: type,
    schema_in: Type[BaseModel],
    prefix: str,
    keyword_columns: Sequence[str] = (),
    extra_filter_columns: Sequence[str] = (),
    on_create: Optional[Callable[[Session, Any, BaseModel], None]] = None,
    on_update: Optional[Callable[[Session, Any, BaseModel], None]] = None,
    response_fields: Optional[Sequence[str]] = None,
) -> APIRouter:
    """生成一组 admin CRUD router。

    on_create / on_update 用于在保存前做额外加工（如哈希密码、级联子表）。
    """
    router = APIRouter(prefix=prefix, tags=[f"admin-{name}"])
    role_dep = Depends(require_role("admin"))

    def _serialize(obj: Any) -> dict:
        if response_fields:
            return {f: getattr(obj, f, None) for f in response_fields}
        cols = {c.name for c in model.__table__.columns}
        return {c: getattr(obj, c, None) for c in cols}

    @router.get("", response_model=Resp[dict])
    def list_items(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=200),
        keyword: Optional[str] = None,
        status_filter: Optional[str] = Query(None, alias="status"),
        enabled_filter: Optional[bool] = Query(None, alias="enabled"),
        db: Session = Depends(get_db),
        _=role_dep,
    ) -> Resp[dict]:
        stmt = select(model)
        if keyword and keyword_columns:
            conds = []
            for col_name in keyword_columns:
                col = getattr(model, col_name, None)
                if col is not None:
                    conds.append(col.ilike(f"%{keyword}%"))
            if conds:
                stmt = stmt.where(or_(*conds))
        if status_filter and "status" in {c.name for c in model.__table__.columns}:
            stmt = stmt.where(getattr(model, "status") == status_filter)
        if enabled_filter is not None and "enabled" in {c.name for c in model.__table__.columns}:
            stmt = stmt.where(getattr(model, "enabled") == enabled_filter)

        # 排序 by id desc
        stmt = stmt.order_by(getattr(model, "id").desc())

        all_items = db.execute(stmt).scalars().all()
        total = len(all_items)
        start = (page - 1) * page_size
        items = all_items[start:start + page_size]
        return Resp(data={
            "items": [_serialize(i) for i in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        })

    @router.get("/{iid}", response_model=Resp[dict])
    def get_item(iid: int, db: Session = Depends(get_db), _=role_dep) -> Resp[dict]:
        obj = db.get(model, iid)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
        return Resp(data=_serialize(obj))

    @router.post("", response_model=Resp[dict])
    def create_item(
        payload: schema_in,
        db: Session = Depends(get_db),
        _=role_dep,
    ) -> Resp[dict]:
        data = payload.model_dump(exclude_none=False)
        # 过滤 model 表中存在的列
        cols = {c.name for c in model.__table__.columns}
        kwargs = {k: v for k, v in data.items() if k in cols}
        obj = model(**kwargs)
        db.add(obj)
        db.flush()
        if on_create:
            on_create(db, obj, payload)
        db.commit()
        db.refresh(obj)
        return Resp(data=_serialize(obj))

    @router.put("/{iid}", response_model=Resp[dict])
    def update_item(
        iid: int,
        payload: schema_in,
        db: Session = Depends(get_db),
        _=role_dep,
    ) -> Resp[dict]:
        obj = db.get(model, iid)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
        data = payload.model_dump(exclude_none=True)
        cols = {c.name for c in model.__table__.columns}
        for k, v in data.items():
            if k in cols:
                setattr(obj, k, v)
        if on_update:
            on_update(db, obj, payload)
        db.commit()
        db.refresh(obj)
        return Resp(data=_serialize(obj))

    @router.delete("/{iid}", response_model=Resp[dict])
    def delete_item(iid: int, db: Session = Depends(get_db), _=role_dep) -> Resp[dict]:
        obj = db.get(model, iid)
        if not obj:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
        db.delete(obj)
        db.commit()
        return Resp(data={"deleted": iid})

    if "enabled" in {c.name for c in model.__table__.columns}:
        @router.post("/{iid}/toggle", response_model=Resp[dict])
        def toggle(iid: int, db: Session = Depends(get_db), _=role_dep) -> Resp[dict]:
            obj = db.get(model, iid)
            if not obj:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="not found")
            obj.enabled = not bool(obj.enabled)
            db.commit()
            return Resp(data={"id": iid, "enabled": obj.enabled})

    return router
