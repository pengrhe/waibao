# -*- coding: utf-8 -*-
"""
安全隐患检查自动化系统 — FastAPI 后端服务入口
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db
from routers.projects import router as projects_router
from config import UPLOAD_DIR

app = FastAPI(
    title="安全隐患检查自动化系统",
    description="Excel解析 → 照片管理 → Word文档自动生成",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir, html=True), name="static")

admin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mockup")
if os.path.exists(admin_dir):
    app.mount("/mockup", StaticFiles(directory=admin_dir, html=True), name="mockup")


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def root():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/admin.html")
