@echo off
chcp 65001 > nul
setlocal

cd /d %~dp0

set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

if not exist .venv (
    echo [aitee-backend] creating venv...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

if not exist .venv\.installed (
    echo [aitee-backend] installing requirements...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    type nul > .venv\.installed
)

if not exist .env (
    echo [aitee-backend] copy .env.example to .env
    copy .env.example .env > nul
)

if not exist aitee.db (
    echo [aitee-backend] running alembic upgrade head...
    alembic upgrade head
)

echo [aitee-backend] starting uvicorn on http://localhost:8200
REM 不加 --reload：避免 reloader + worker 双进程结构，stop.bat 单 PID 即可干净杀掉
uvicorn app.main:app --host 0.0.0.0 --port 8200
