@echo off
chcp 936 >nul
title Safety Check System - Backend

echo ============================================
echo   Safety Check System - Start Backend
echo ============================================
echo.

rem Kill existing uvicorn processes on port 8900
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='python.exe' and CommandLine like '%%8900%%'" get ProcessId /format:csv 2^>nul ^| findstr /R "[0-9]"') do (
    echo [WARN] Killing existing uvicorn ^(PID: %%a^)...
    taskkill /f /pid %%a /T >nul 2>&1
)

rem Kill orphaned workers still on port 8900
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8900 " ^| findstr "LISTEN"') do (
    echo [WARN] Killing remaining process on port 8900 ^(PID: %%a^)...
    taskkill /f /pid %%a /T >nul 2>&1
    for /f "tokens=2 delims=," %%b in ('wmic process where "ParentProcessId=%%a" get ProcessId /format:csv 2^>nul ^| findstr /R "[0-9]"') do (
        taskkill /f /pid %%b >nul 2>&1
    )
)

timeout /t 2 /nobreak >nul

cd /d "%~dp0backend"

echo [INFO] Starting FastAPI...
echo [INFO] URL: http://localhost:8900
echo [INFO] Docs: http://localhost:8900/docs
echo [INFO] Press Ctrl+C to stop
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8900