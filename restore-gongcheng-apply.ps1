param(
    [string]$HistoryRoot      = "C:\Users\admin\AppData\Roaming\Cursor\User\History",
    [string]$UriPrefix        = "d%3A/wp/waibao/gongcheng/",
    [datetime]$RollbackMoment = [datetime]"2026-05-27 11:48:58",
    [int]$ToleranceSec        = 2,
    [string]$BackupRoot       = "D:\wp\waibao\.restore-backup",
    [switch]$DryRun
)

$rollMs = [DateTimeOffset]::new($RollbackMoment, [TimeSpan]::FromHours(8)).ToUnixTimeMilliseconds()
$tolMs = $ToleranceSec * 1000

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $BackupRoot $stamp
if (-not $DryRun) {
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
}
Write-Host ("Rollback moment: {0} CST ({1} ms +/- {2} ms)" -f $RollbackMoment, $rollMs, $tolMs)
Write-Host ("Backup dir     : {0}" -f $backupDir)
Write-Host ("DryRun         : {0}" -f $DryRun.IsPresent)
Write-Host ""

$entriesFiles = Get-ChildItem -Path $HistoryRoot -Recurse -Filter "entries.json" -ErrorAction SilentlyContinue

$plan = New-Object System.Collections.Generic.List[object]
foreach ($ef in $entriesFiles) {
    $raw = Get-Content -LiteralPath $ef.FullName -Raw -Encoding UTF8
    if ($raw -notmatch [regex]::Escape($UriPrefix)) { continue }
    try { $json = $raw | ConvertFrom-Json } catch { continue }
    if (-not $json.resource) { continue }
    if ($json.resource -notlike "file:///$UriPrefix*") { continue }

    $entries = @($json.entries) | Sort-Object timestamp
    if ($entries.Count -lt 2) { continue }
    $latest = $entries[-1]
    if ([Math]::Abs([int64]$latest.timestamp - [int64]$rollMs) -gt $tolMs) { continue }

    $prev = $entries[-2]
    $relUri = $json.resource.Substring("file:///".Length)
    $filePath = ([System.Uri]::UnescapeDataString($relUri)) -replace '/', '\'

    $latestSnap = Join-Path $ef.DirectoryName $latest.id
    $prevSnap   = Join-Path $ef.DirectoryName $prev.id

    $plan.Add([pscustomobject]@{
        File         = $filePath
        CurrLen      = if (Test-Path -LiteralPath $filePath) { (Get-Item -LiteralPath $filePath).Length } else { -1 }
        LatestId     = $latest.id
        LatestTs     = [DateTimeOffset]::FromUnixTimeMilliseconds($latest.timestamp).ToOffset([TimeSpan]::FromHours(8)).ToString("yyyy-MM-dd HH:mm:ss")
        LatestLen    = if (Test-Path -LiteralPath $latestSnap) { (Get-Item -LiteralPath $latestSnap).Length } else { -1 }
        PrevId       = $prev.id
        PrevTs       = [DateTimeOffset]::FromUnixTimeMilliseconds($prev.timestamp).ToOffset([TimeSpan]::FromHours(8)).ToString("yyyy-MM-dd HH:mm:ss")
        PrevLen      = if (Test-Path -LiteralPath $prevSnap) { (Get-Item -LiteralPath $prevSnap).Length } else { -1 }
        PrevSnapPath = $prevSnap
    })
}

Write-Host ("Files matching rollback moment: {0}" -f $plan.Count)
Write-Host ""
$plan | Format-Table File, CurrLen, LatestLen, LatestTs, PrevLen, PrevTs -AutoSize | Out-String -Width 4096 | Write-Host

if ($DryRun) {
    Write-Host "[DryRun] No files were modified."
    return
}

foreach ($row in $plan) {
    if (-not (Test-Path -LiteralPath $row.PrevSnapPath)) {
        Write-Warning ("Skip {0}: prev snapshot not found" -f $row.File)
        continue
    }

    if (Test-Path -LiteralPath $row.File) {
        $rel = $row.File.Substring("D:\wp\waibao\gongcheng\".Length)
        $bk = Join-Path $backupDir $rel
        New-Item -ItemType Directory -Path (Split-Path -Parent $bk) -Force | Out-Null
        Copy-Item -LiteralPath $row.File -Destination $bk -Force
    }

    Copy-Item -LiteralPath $row.PrevSnapPath -Destination $row.File -Force
    Write-Host ("Restored: {0}  ({1} bytes -> {2} bytes, snap {3})" -f $row.File, $row.CurrLen, $row.PrevLen, $row.PrevTs)
}

Write-Host ""
Write-Host ("Done. Current versions backed up to: {0}" -f $backupDir)
