from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Literal, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Realm = Literal["c", "b"]


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def _secret(realm: Realm) -> str:
    return settings.JWT_SECRET_C if realm == "c" else settings.JWT_SECRET_B


def create_access_token(
    subject: str,
    realm: Realm,
    extra: Optional[Dict[str, Any]] = None,
    expire_minutes: Optional[int] = None,
) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=expire_minutes or settings.JWT_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": subject,
        "realm": realm,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, _secret(realm), algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, realm: Realm) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, _secret(realm), algorithms=[settings.JWT_ALGORITHM])
    except JWTError as e:
        raise ValueError(f"invalid token: {e}") from e
    if payload.get("realm") != realm:
        raise ValueError("realm mismatch")
    return payload
