"""C 端扫码接口（伙伴推广 / 门店下单 / 城市分享）。

二维码图片由前端用 vue-qrcode / wxbarcode 渲染，后端只发 code + target_url。
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Partner, QrCode, Store, StoreStaff
from app.schemas.common import Resp

router = APIRouter(prefix="/qr", tags=["c-qrcode"])


@router.get("/{code}", response_model=Resp[dict])
def scan(code: str, db: Session = Depends(get_db)) -> Resp[dict]:
    qr = db.execute(select(QrCode).where(QrCode.code == code, QrCode.enabled == True)).scalar_one_or_none()  # noqa: E712
    if not qr:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="二维码无效")
    qr.scan_count += 1
    db.commit()

    out: dict = {
        "code": qr.code,
        "type": qr.type,
        "target_url": qr.target_url,
        "owner_type": qr.owner_type,
        "owner_id": qr.owner_id,
        "style": qr.style,
        "extra": {},
    }
    if qr.owner_type == "partner" and qr.owner_id:
        p = db.get(Partner, qr.owner_id)
        if p:
            out["extra"] = {"partner_name": p.name, "channel": p.channel}
    elif qr.owner_type == "store" and qr.owner_id:
        s = db.get(Store, qr.owner_id)
        if s:
            out["extra"] = {"store_name": s.name, "city": s.city, "address": s.address}
    elif qr.owner_type == "staff" and qr.owner_id:
        st = db.get(StoreStaff, qr.owner_id)
        if st:
            out["extra"] = {"staff_name": st.name, "store_id": st.store_id}
    return Resp(data=out)
