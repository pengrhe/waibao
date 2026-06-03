@echo off
REM aitee port status (5 services after B-merge)
echo.
echo  ============= aitee port status =============
call :check 8200 backend
call :check 8201 frontend
call :check 8202 admin
call :check 8203 portal
call :check 8206 miniapp-h5
echo.
exit /b 0

:check
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$port=%1; $name='%2'; $c = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1; if ($c) { $proc = Get-Process -Id $c.OwningProcess -ErrorAction SilentlyContinue; $pn = if ($proc) { $proc.ProcessName } else { '?' }; Write-Host ('  {0}  {1,-12}  RUNNING  PID {2,-6} ({3})' -f $port, $name, $c.OwningProcess, $pn) -ForegroundColor Green } else { Write-Host ('  {0}  {1,-12}  FREE' -f $port, $name) -ForegroundColor DarkGray }"
exit /b 0
