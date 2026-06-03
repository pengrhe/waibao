@echo off
REM ============================================================
REM  aitee - restart one service by name (kill by port + relaunch)
REM  Usage:
REM    restart.bat                 Show usage
REM    restart.bat backend         Restart backend  (8200)
REM    restart.bat frontend        Restart C-H5     (8201)
REM    restart.bat admin           Restart admin    (8202)
REM    restart.bat portal          Restart portal   (8203, partner/store/staff)
REM    restart.bat miniapp         Restart miniapp-h5 (8206)
REM ============================================================
setlocal

set "SERVICE=%~1"
set "PORT="
set "DIR="
set "CMD="

if /i "%SERVICE%"=="backend"  ( set "PORT=8200" & set "DIR=backend"   & set "CMD=start.bat" )
if /i "%SERVICE%"=="frontend" ( set "PORT=8201" & set "DIR=frontend"  & set "CMD=start.bat" )
if /i "%SERVICE%"=="admin"    ( set "PORT=8202" & set "DIR=admin"     & set "CMD=start.bat" )
if /i "%SERVICE%"=="portal"   ( set "PORT=8203" & set "DIR=b-portals" & set "CMD=npm run dev" )
if /i "%SERVICE%"=="miniapp"  ( set "PORT=8206" & set "DIR=miniapp"   & set "CMD=npm run dev:h5" )

if "%PORT%"=="" (
    echo.
    echo Usage: restart.bat [backend^|frontend^|admin^|portal^|miniapp]
    echo.
    echo Examples:
    echo   restart.bat backend
    echo   restart.bat portal
    echo.
    exit /b 1
)

echo.
echo [aitee-restart] %SERVICE% (port %PORT%)
echo   1) stopping ...
call "%~dp0stop.bat" %PORT%

echo   2) waiting port release ...
timeout /t 1 /nobreak > nul

echo   3) starting in new window ...
pushd "%~dp0%DIR%"
if /i "%CMD%"=="start.bat" (
    start "aitee-%SERVICE% (%PORT%)" cmd /k start.bat
) else (
    start "aitee-%SERVICE% (%PORT%)" cmd /k "set PATH=C:\nvm4w\nodejs;%%PATH%% && %CMD%"
)
popd

echo.
echo [aitee-restart] launched %SERVICE% in new window, port %PORT%
echo                 wait 5-10s then visit http://localhost:%PORT%/

endlocal
