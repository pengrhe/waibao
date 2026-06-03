"""C 端登录（M2 mock 模式 + 真 wx/dy 接入口子）。"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import User


def mock_login(
    db: Session,
    *,
    channel: str = "h5",
    phone: Optional[str] = None,
    nickname: Optional[str] = None,
) -> Tuple[str, User]:
    """M2 阶段 mock 登录：按手机号 upsert 用户，不验证码。

    M3 接真渠道时：
      - wx_app：用 code 换 openid → 找/建用户
      - dy_app：抖音 code → openid
    """
    user: Optional[User] = None
    if phone:
        user = db.execute(select(User).where(User.phone == phone)).scalar_one_or_none()

    if not user:
        user = User(
            phone=phone or f"mock_{int(datetime.now(timezone.utc).timestamp())}",
            nickname=nickname or "aitee 用户",
            status="active",
        )
        db.add(user)
        db.flush()

    if nickname and user.nickname != nickname:
        user.nickname = nickname

    user.last_login_at = datetime.now(timezone.utc)
    db.flush()

    token = create_access_token(
        subject=str(user.id),
        realm="c",
        extra={"channel": channel},
    )
    return token, user
