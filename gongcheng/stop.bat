@echo off
chcp 936 >nul

echo ============================================
echo   Safety Check System - Stop Backend
echo ============================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0stop-port.ps1" -Port 8900
set RC=%ERRORLEVEL%

echo.
if "%RC%"=="0" (
    echo [DONE] Backend service stopped.
) else (
    echo [WARN] Stop script exited with code %RC%. You may need to run as Administrator.
)

echo.
pause