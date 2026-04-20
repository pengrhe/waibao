@echo off
chcp 936 >nul

echo ============================================
echo   Safety Check System - Stop Backend
echo ============================================
echo.

set killed=0

rem 1) Kill uvicorn processes related to port 8900 (reloader + worker)
for /f "tokens=2 delims=," %%a in ('wmic process where "Name='python.exe' and CommandLine like '%%8900%%'" get ProcessId /format:csv 2^>nul ^| findstr /R "[0-9]"') do (
    echo [INFO] Killing uvicorn process ^(PID: %%a^)...
    taskkill /f /pid %%a /T >nul 2>&1
    set killed=1
)

rem 2) Kill any orphaned multiprocessing workers still holding port 8900
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr ":8900 " ^| findstr "LISTEN"') do (
    echo [INFO] Killing remaining process on port 8900 ^(PID: %%a^)...
    taskkill /f /pid %%a /T >nul 2>&1
    rem Also kill by PID directly in case /T misses it
    for /f "tokens=2 delims=," %%b in ('wmic process where "ParentProcessId=%%a" get ProcessId /format:csv 2^>nul ^| findstr /R "[0-9]"') do (
        echo [INFO] Killing child process ^(PID: %%b^)...
        taskkill /f /pid %%b >nul 2>&1
    )
    set killed=1
)

if "%killed%"=="0" (
    echo [INFO] No running backend service found.
) else (
    timeout /t 2 /nobreak >nul
    echo [INFO] Backend service stopped.
)

echo.
pause