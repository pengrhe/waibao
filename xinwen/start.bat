@echo off
chcp 936 >nul
title Xinwen News System - Service
cd /d "%~dp0"

echo ============================================
echo   Xinwen News System - Start Service
echo ============================================
echo.

rem Kill existing process on port 5501
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":5501 " ^| findstr "LISTEN"') do (
    echo [WARN] Killing existing process on port 5501 ^(PID: %%a^)...
    taskkill /f /pid %%a /T >nul 2>&1
)

timeout /t 2 /nobreak >nul

rem Set environment variables
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
set XINWEN_API_PORT=5501

echo [INFO] Starting Xinwen News Service...
echo [INFO] URL: http://localhost:5501
echo [INFO] Crawl schedule: 06:30 daily
echo [INFO] WeChat send schedule: 07:00 daily
echo [INFO] Press Ctrl+C to stop
echo.

python -m uvicorn main:app --host 0.0.0.0 --port 5501
pause
