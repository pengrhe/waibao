param(
    [string]$HistoryRoot = "C:\Users\admin\AppData\Roaming\Cursor\User\History",
    [string]$PathPrefix  = "d:/wp/waibao/gongcheng/",
    [string]$UriPrefix   = "d%3A/wp/waibao/gongcheng/",
    [datetime]$Threshold = [datetime]"2026-05-25 09:00:00",
    [string]$ReportPath  = "D:\wp\waibao\restore-gongcheng-plan.csv"
)

$thresholdMs = [DateTimeOffset]::new($Threshold, [TimeSpan]::FromHours(8)).ToUnixTimeMilliseconds()
Write-Host ("Threshold = {0} CST ({1} ms)" -f $Threshold, $thresholdMs)
Write-Host ("History root = {0}" -f $HistoryRoot)
Write-Host ("Path prefix  = {0}" -f $PathPrefix)
Write-Host ""

$rows = New-Object System.Collections.Generic.List[object]
$entriesFiles = Get-ChildItem -Path $HistoryRoot -Recurse -Filter "entries.json" -ErrorAction SilentlyContinue
Write-Host ("Total entries.json files: {0}" -f $entriesFiles.Count)

$matched = 0
foreach ($ef in $entriesFiles) {
    $raw = Get-Content -LiteralPath $ef.FullName -Raw -Encoding UTF8
    if ($raw -notmatch [regex]::Escape($UriPrefix)) { continue }
    $matched++

    try { $json = $raw | ConvertFrom-Json } catch { continue }
    $resource = $json.resource
    if (-not $resource) { continue }
    if ($resource -notlike "file:///$UriPrefix*") { continue }

    $relUri = $resource.Substring("file:///".Length)
    $decoded = [System.Uri]::UnescapeDataString($relUri)
    $filePath = $decoded -replace '/', '\'

    $entries = @($json.entries) | Sort-Object timestamp
    if ($entries.Count -eq 0) { continue }

    $latestBefore = $entries | Where-Object { $_.timestamp -lt $thresholdMs } | Select-Object -Last 1
    $latestOverall = $entries | Select-Object -Last 1

    $currExists = Test-Path -LiteralPath $filePath
    $currLen = if ($currExists) { (Get-Item -LiteralPath $filePath).Length } else { -1 }
    $currMtime = if ($currExists) { (Get-Item -LiteralPath $filePath).LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss") } else { "" }

    $snapPath = $null
    $snapLen = -1
    $snapTs = ""
    if ($latestBefore) {
        $snapPath = Join-Path -Path $ef.DirectoryName -ChildPath $latestBefore.id
        if (Test-Path -LiteralPath $snapPath) {
            $snapLen = (Get-Item -LiteralPath $snapPath).Length
        }
        $snapTs = [DateTimeOffset]::FromUnixTimeMilliseconds($latestBefore.timestamp).ToOffset([TimeSpan]::FromHours(8)).ToString("yyyy-MM-dd HH:mm:ss")
    }

    $latestTs = [DateTimeOffset]::FromUnixTimeMilliseconds($latestOverall.timestamp).ToOffset([TimeSpan]::FromHours(8)).ToString("yyyy-MM-dd HH:mm:ss")

    $needRestore = $false
    if ($latestBefore) {
        if (-not $currExists) {
            $needRestore = $true
        } elseif ($snapLen -ne $currLen) {
            $needRestore = $true
        } else {
            $a = Get-FileHash -LiteralPath $filePath -Algorithm SHA1
            $b = Get-FileHash -LiteralPath $snapPath -Algorithm SHA1
            if ($a.Hash -ne $b.Hash) { $needRestore = $true }
        }
    }

    $rows.Add([pscustomobject]@{
        File          = $filePath
        CurrExists    = $currExists
        CurrLen       = $currLen
        CurrMtime     = $currMtime
        LatestSnap    = $latestTs
        SnapBeforeTs  = $snapTs
        SnapBeforeId  = if ($latestBefore) { $latestBefore.id } else { "" }
        SnapBeforeLen = $snapLen
        NeedRestore   = $needRestore
        HistoryDir    = $ef.DirectoryName
    })
}

Write-Host ("Matched gongcheng entries: {0}" -f $matched)
Write-Host ("Files needing restore   : {0}" -f ($rows | Where-Object { $_.NeedRestore }).Count)
Write-Host ""
Write-Host "=== Files needing restore ==="
$rows | Where-Object { $_.NeedRestore } |
    Sort-Object File |
    Select-Object File, CurrLen, SnapBeforeLen, CurrMtime, SnapBeforeTs, LatestSnap |
    Format-Table -AutoSize | Out-String -Width 4096 | Write-Host

$rows | Export-Csv -LiteralPath $ReportPath -NoTypeInformation -Encoding UTF8
Write-Host ("Full plan saved to: {0}" -f $ReportPath)
