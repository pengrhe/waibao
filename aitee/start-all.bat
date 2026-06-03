@echo off
REM ============================================================
REM  aitee - start all 5 services (each in its own cmd window)
REM ============================================================

echo.
echo [aitee-start-all] launching 5 services, each in its own window
echo.

pushd "%~dp0backend"
start "aitee-backend (8200)" cmd /k start.bat
popd
timeout /t 2 /nobreak > nul

pushd "%~dp0frontend"
start "aitee-frontend (8201)" cmd /k start.bat
popd
timeout /t 1 /nobreak > nul

pushd "%~dp0admin"
start "aitee-admin (8202)" cmd /k start.bat
popd
timeout /t 1 /nobreak > nul

pushd "%~dp0b-portals"
start "aitee-portal (8203)" cmd /k "set PATH=C:\nvm4w\nodejs;%%PATH%% && npm run dev"
popd
timeout /t 1 /nobreak > nul

pushd "%~dp0miniapp"
start "aitee-miniapp-h5 (8206)" cmd /k "set PATH=C:\nvm4w\nodejs;%%PATH%% && npm run dev:h5"
popd

echo.
echo [aitee-start-all] all triggered, wait 10-30 seconds.
echo                   run status.bat to check ports.
echo                   run stop.bat (no args) to stop all.
echo.
