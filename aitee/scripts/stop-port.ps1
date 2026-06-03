# aitee - 安全按端口杀进程
# Usage: powershell -File stop-port.ps1 <port>
#
# 策略：
# 1. 通过 Get-NetTCPConnection 拿监听该端口的 PID
# 2. 对每个 PID：用 taskkill /F /T 杀整个进程树（兼容 npm/vite/uvicorn 这类 spawn child 的工具）
# 3. 如果 taskkill 失败（PID 已死但 socket 残留），fallback 用 Stop-Process

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [int]$Port
)

$conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if (-not $conns) {
    Write-Host ("  port {0,5} : free" -f $Port) -ForegroundColor DarkGray
    exit 0
}

$pids = $conns.OwningProcess | Sort-Object -Unique
foreach ($pp in $pids) {
    $proc = Get-Process -Id $pp -ErrorAction SilentlyContinue
    $pname = if ($proc) { $proc.ProcessName } else { "(dead)" }

    if (-not $proc) {
        # 进程已死但 socket 残留，无能为力，只能等 TCP 回收
        Write-Host ("  port {0,5} : PID {1} already dead (socket lingering, will release soon)" -f $Port, $pp) -ForegroundColor DarkYellow
        continue
    }

    # 用 taskkill 杀进程树（包括 cmd 窗口启动的子 uvicorn / vite / node）
    $tk = & taskkill /F /T /PID $pp 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host ("  port {0,5} : killed PID {1} ({2}) [tree]" -f $Port, $pp, $pname) -ForegroundColor Yellow
    } else {
        # fallback: 直接 Stop-Process
        try {
            Stop-Process -Id $pp -Force -ErrorAction Stop
            Write-Host ("  port {0,5} : killed PID {1} ({2}) [single]" -f $Port, $pp, $pname) -ForegroundColor Yellow
        } catch {
            Write-Host ("  port {0,5} : PID {1} ({2}) kill FAIL: {3}" -f $Port, $pp, $pname, $_.Exception.Message) -ForegroundColor Red
        }
    }
}
