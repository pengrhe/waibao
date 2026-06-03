from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base
from app.models._base import IdMixin, TimestampMixin


class AdminUser(IdMixin, TimestampMixin, Base):
    """总部管理员账号。与 C 端 users 完全隔离。"""

    __tablename__ = "admin_users"

    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    real_name: Mapped[Optional[str]] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(String(16), default="admin")  # superadmin/admin/audit/finance
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(64))
