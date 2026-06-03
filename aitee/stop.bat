@echo off
REM ============================================================
REM  aitee - kill process by port (safe, no batch python kill)
REM  Usage:
REM    stop.bat                    Kill all aitee ports
REM    stop.bat 8200               Kill one
REM    stop.bat 8202 8203          Kill several
REM
REM  Active ports (5 services after B-merge):
REM    8200 backend
REM    8201 frontend C-side H5
REM    8202 admin
REM    8203 portal (partner/store/staff merged)
REM    8206 miniapp-h5
REM ============================================================
setlocal enabledelayedexpansion

if "%~1"=="" (
    set "PORTS=8200 8201 8202 8203 8206"
    echo [aitee-stop] no args, killing ALL aitee ports
) else (
    set "PORTS=%*"
)

for %%P in (!PORTS!) do (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\stop-port.ps1" %%P
)

endlocal
