@echo off
chcp 936 >nul
title Safety Check Backend

echo ============================================
echo   Safety Check System - Start Backend
echo ============================================
echo.

echo [INFO] Stopping any existing backend on port 8900...
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-port.ps1" -Port 8900
if errorlevel 1 (
    echo [ERROR] Failed to release port 8900. Aborting start.
    pause
    exit /b 1
)

cd /d "%~dp0backend"

echo.
echo [INFO] Starting FastAPI...
echo [INFO] URL : http://localhost:8900
echo [INFO] Docs: http://localhost:8900/docs
echo [INFO] Press Ctrl+C to stop.
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8900