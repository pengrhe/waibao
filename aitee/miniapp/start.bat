@echo off
chcp 65001 > nul
setlocal
cd /d %~dp0
set PATH=C:\nvm4w\nodejs;%PATH%
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890

if not exist node_modules (
    echo [miniapp] installing deps via proxy...
    npm install
)

echo [miniapp] 用法：
echo   npm run dev:h5            ^(http://localhost:8206, 浏览器预览^)
echo   npm run dev:mp-weixin     ^(编译 dist/dev/mp-weixin, 用微信开发者工具打开^)
echo   npm run dev:mp-toutiao    ^(编译 dist/dev/mp-toutiao, 用抖音开发者工具打开^)
