from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import b_portals_auth, health, payments
from app.routers.admin import all_routers as admin_routers
from app.routers.c import all_routers as c_routers


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        debug=settings.APP_DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_origin_regex=r"http://(localhost|127\.0\.0\.1):\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory=settings.UPLOAD_DIR), name="static")

    # 前端 UI 静态资源（H5/小程序共用，避免小程序包内打包 30MB+ PNG）
    # 物理目录：<repo-root>/aitee/cdn-assets
    cdn_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "cdn-assets")
    )
    if os.path.isdir(cdn_dir):
        app.mount("/cdn", StaticFiles(directory=cdn_dir), name="cdn")

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(b_portals_auth.partner_router, prefix="/api/v1")
    app.include_router(b_portals_auth.store_router, prefix="/api/v1")
    app.include_router(b_portals_auth.staff_router, prefix="/api/v1")

    # Admin 后台路由
    for r in admin_routers:
        app.include_router(r, prefix="/api/v1")

    # C 端业务接口
    for r in c_routers:
        app.include_router(r, prefix="/api/v1")

    # Mock 支付回调
    app.include_router(payments.router, prefix="/api/v1")

    @app.get("/")
    def root():
        return {
            "name": settings.APP_NAME,
            "env": settings.APP_ENV,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    return app


app = create_app()
