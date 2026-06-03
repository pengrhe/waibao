@echo off
chcp 65001 > nul
setlocal
cd /d %~dp0
set PATH=C:\nvm4w\nodejs;%PATH%
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

if not exist node_modules (
    echo [b-portals] installing workspace deps via proxy...
    npm install
)

echo [b-portals] portal (partner+store+staff) on http://localhost:8203
npm run dev
