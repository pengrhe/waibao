# -*- Stop all processes related to the given TCP port -*-
# Kills:
#   1) Process(es) currently LISTENing on the port (uvicorn worker)
#   2) Their parent process (uvicorn --reload reloader)
#   3) The whole process tree rooted at the above (recursive)
#   4) Any python.exe whose command line still contains the port number
#      (paranoia fallback in case netstat missed something)
#
# Usage:  powershell -NoProfile -ExecutionPolicy Bypass -File stop-port.ps1 -Port 8900

param(
    [int]$Port = 8900
)

$ErrorActionPreference = 'SilentlyContinue'

function Get-Descendants {
    param([int]$RootPid, [hashtable]$ProcMap)
    $result = New-Object System.Collections.Generic.List[int]
    $queue  = New-Object System.Collections.Generic.Queue[int]
    $queue.Enqueue($RootPid)
    while ($queue.Count -gt 0) {
        $cur = $queue.Dequeue()
        if ($ProcMap.ContainsKey($cur)) {
            foreach ($child in $ProcMap[$cur]) {
                $result.Add($child) | Out-Null
                $queue.Enqueue($child)
            }
        }
    }
    return $result
}

# Build PID -> children map once
$allProcs = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue
$procMap = @{}
foreach ($p in $allProcs) {
    $ppid = [int]$p.ParentProcessId
    if (-not $procMap.ContainsKey($ppid)) {
        $procMap[$ppid] = New-Object System.Collections.Generic.List[int]
    }
    $procMap[$ppid].Add([int]$p.ProcessId) | Out-Null
}

$targets = New-Object System.Collections.Generic.HashSet[int]

# 1) PIDs LISTENing on the port
$conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
foreach ($c in $conns) {
    $owner = [int]$c.OwningProcess
    if ($owner -gt 4) { [void]$targets.Add($owner) }
    # parent of the listening worker = uvicorn reloader
    $parent = ($allProcs | Where-Object { $_.ProcessId -eq $owner } | Select-Object -First 1).ParentProcessId
    if ($parent -and [int]$parent -gt 4) { [void]$targets.Add([int]$parent) }
}

# 2) python.exe whose command line references the port (covers reloader
#    process that does not listen, and any leftover workers)
$pyProcs = $allProcs | Where-Object {
    $_.Name -eq 'python.exe' -and $_.CommandLine -and ($_.CommandLine -like "*$Port*")
}
foreach ($p in $pyProcs) {
    [void]$targets.Add([int]$p.ProcessId)
}

# 3) Expand to whole process tree
$expanded = New-Object System.Collections.Generic.HashSet[int]
foreach ($t in $targets) {
    [void]$expanded.Add($t)
    foreach ($d in Get-Descendants -RootPid $t -ProcMap $procMap) {
        [void]$expanded.Add($d)
    }
}

if ($expanded.Count -eq 0) {
    Write-Host "[INFO] No backend process found on port $Port."
    exit 0
}

# 4) Kill from leaves up (children first) to avoid reloader respawning
$sorted = $expanded | Sort-Object -Descending
foreach ($p in $sorted) {
    $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
    if ($proc) {
        Write-Host ("[INFO] Killing PID {0} ({1})" -f $p, $proc.ProcessName)
        Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
    }
}

# 5) Wait for the port to actually be released (max 10s)
for ($i = 0; $i -lt 20; $i++) {
    Start-Sleep -Milliseconds 500
    $still = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if (-not $still) {
        Write-Host "[INFO] Port $Port released."
        exit 0
    }
}

Write-Host "[WARN] Port $Port is still in use after kill attempts."
exit 1
