@echo off
chcp 65001 >nul
title aitee frontend dev server
cd /d "%~dp0"

REM 加上常见 nodejs 安装路径，防止找不到 npm
set PATH=C:\nvm4w\nodejs;C:\Program Files\nodejs;%APPDATA%\npm;%PATH%

if not exist node_modules (
  echo.
  echo [INFO] node_modules 不存在，先安装依赖（约 1 分钟）...
  set HTTP_PROXY=http://127.0.0.1:7890
  set HTTPS_PROXY=http://127.0.0.1:7890
  call npm install --no-audit --no-fund
  if errorlevel 1 (
    echo [ERROR] npm install 失败
    pause
    exit /b 1
  )
)

echo.
echo ============================================
echo   aitee frontend - 启动 Vite Dev Server
echo ============================================
echo   电脑访问  : http://localhost:8201
echo   手机访问  : 见终端 Network 那一行
echo   F12 切移动设备模拟（推荐 iPhone 12 Pro）
echo   Ctrl + C 停止
echo ============================================
echo.

call npm run dev -- --host
