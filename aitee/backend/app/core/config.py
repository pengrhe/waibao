from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    APP_ENV: str = "dev"
    APP_NAME: str = "aitee-backend"
    APP_DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./aitee.db"
    REDIS_URL: Optional[str] = None

    JWT_SECRET_C: str = "dev-secret-c"
    JWT_SECRET_B: str = "dev-secret-b"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24 * 7

    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = "google/gemini-3-pro"

    UPLOAD_DIR: str = "./uploads"
    PUBLIC_BASE_URL: str = "http://localhost:8200"

    CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:8201",  # frontend C 端 H5
            "http://localhost:8202",  # admin 总部后台
            "http://localhost:8203",  # portal 业务端（partner/store/staff 合一）
            "http://localhost:8206",  # miniapp h5 预览
        ]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
