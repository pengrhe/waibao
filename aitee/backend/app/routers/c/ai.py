from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.deps.c_user import get_optional_user
from app.models import User
from app.schemas.c import AiGenerateIn, AiGenerateOut, AiSampleOut
from app.schemas.common import Resp
from app.services.ai_service import generate

router = APIRouter(prefix="/ai", tags=["c-ai"])


STYLES = ["国潮", "极简", "Y2K", "赛博朋克", "水彩", "像素", "3D", "复古"]


@router.get("/styles", response_model=Resp[List[str]])
def styles() -> Resp[List[str]]:
    return Resp(data=STYLES)


@router.post("/generate", response_model=Resp[AiGenerateOut])
async def ai_generate(
    payload: AiGenerateIn,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
) -> Resp[AiGenerateOut]:
    samples, fallback, status_ = await generate(
        db,
        user_id=user.id if user else None,
        type_=payload.type,
        prompt=payload.prompt,
        style=payload.style,
        source_image_url=payload.source_image_url,
        n=payload.n,
    )
    return Resp(data=AiGenerateOut(
        samples=[AiSampleOut(**s) for s in samples],
        status=status_,
        fallback=fallback,
    ))
