# ==============================================================================
# BEOMCHRO v2.1 Pure Windows Native Controller (Zero-Python Required!)
# Runs on any Windows 10/11 PC out-of-the-box using built-in .NET & PowerShell
# ==============================================================================

$ErrorActionPreference = "SilentlyContinue"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ExtDir = Join-Path $ScriptDir "extension"
$SimDir = Join-Path $ScriptDir "simulator"
$ProfileDir = Join-Path $env:USERPROFILE ".beomchro\browser_profile"
$Port = 8989

# 1. Detect installed Chromium browser (Chrome / Edge / Whale / Brave)
function Find-Browser {
    $candidates = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
        "$env:ProgramFiles\Naver\Naver Whale\Application\whale.exe",
        "$env:LOCALAPPDATA\Naver\Naver Whale\Application\whale.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe"
    )
    foreach ($p in $candidates) {
        if (Test-Path $p) { return $p }
    }
    return $null
}

# 2. Start background lightweight HTTP Server on 127.0.0.1:8989 using TcpListener (No Admin Rights Needed)
$ServerJob = Start-Job -ScriptBlock {
    param($SimDir, $ExtDir, $Port)
    try {
        $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
        $listener.Start()
        while ($true) {
            $client = $listener.AcceptTcpClient()
            $stream = $client.GetStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $requestLine = $reader.ReadLine()
            if ($requestLine) {
                while ($reader.ReadLine() -ne "") {}
                $parts = $requestLine.Split(" ")
                $reqPath = if ($parts.Length -ge 2) { $parts[1].Split("?")[0] } else { "/" }
                if ($reqPath -eq "/") { $reqPath = "/index.html" }

                $filePath = $null
                $contentType = "text/html; charset=utf-8"

                if ($reqPath -eq "/extension/content.js") {
                    $filePath = Join-Path $ExtDir "content.js"
                    $contentType = "application/javascript; charset=utf-8"
                } else {
                    $relPath = $reqPath.TrimStart("/").Replace("/", "\")
                    $filePath = Join-Path $SimDir $relPath
                    if ($reqPath.EndsWith(".css")) { $contentType = "text/css; charset=utf-8" }
                    elseif ($reqPath.EndsWith(".js")) { $contentType = "application/javascript; charset=utf-8" }
                }

                if ($filePath -and (Test-Path $filePath)) {
                    $bytes = [System.IO.File]::ReadAllBytes($filePath)
                    $header = "HTTP/1.1 200 OK`r`nContent-Type: $contentType`r`nContent-Length: $($bytes.Length)`r`nAccess-Control-Allow-Origin: *`r`nConnection: close`r`n`r`n"
                    $headerBytes = [System.Text.Encoding]::UTF8.GetBytes($header)
                    $stream.Write($headerBytes, 0, $headerBytes.Length)
                    $stream.Write($bytes, 0, $bytes.Length)
                } else {
                    $notFound = [System.Text.Encoding]::UTF8.GetBytes("HTTP/1.1 404 Not Found`r`nContent-Length: 0`r`nConnection: close`r`n`r`n")
                    $stream.Write($notFound, 0, $notFound.Length)
                }
            }
            $client.Close()
        }
    } catch {}
} -ArgumentList $SimDir, $ExtDir, $Port

$BrowserExe = Find-Browser

while ($true) {
    Clear-Host
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host "  ██████╗ ███████╗ ██████╗ ███╗   ███╗ ██████╗██╗  ██╗██████╗  ██████╗ " -ForegroundColor Cyan
    Write-Host "  ██╔══██╗██╔════╝██╔═══██╗████╗ ████║██╔════╝██║  ██║██╔══██╗██╔═══██╗" -ForegroundColor Cyan
    Write-Host "  ██████╔╝█████╗  ██║   ██║██╔████╔██║██║     ███████║██████╔╝██║   ██║" -ForegroundColor Cyan
    Write-Host "  ██╔══██╗██╔══╝  ██║   ██║██║╚██╔╝██║██║     ██╔══██║██╔══██╗██╔═══██║" -ForegroundColor Cyan
    Write-Host "  ██████╔╝███████╗╚██████╔╝██║ ╚═╝ ██║╚██████╗██║  ██║██║  ██║╚██████╔╝" -ForegroundColor Cyan
    Write-Host "  ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ " -ForegroundColor Cyan
    Write-Host "       >>> NOL-TICKET ULTRA FAST QUEUE INTERCEPTOR v2.1 (Windows) <<<     " -ForegroundColor Yellow
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [시스템 상태]" -ForegroundColor White
    Write-Host "  • 파이썬 없이 즉시 실행 모드 : ACTIVE (Windows Native Engine)" -ForegroundColor Green
    Write-Host "  • 자체 테스트 연습장 서버    : ONLINE (http://localhost:$Port)" -ForegroundColor Green
    Write-Host "  • 감지된 브라우저            : $BrowserExe" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [동작 모드 선택]" -ForegroundColor Yellow
    Write-Host "  1. 🚀 원클릭 0ms 티켓팅 브라우저 & 2026 한국시리즈 7차전 자체 테스트 실행 (기본 권장)" -ForegroundColor Green
    Write-Host "  0. ❌ 프로그램 종료 (Exit)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  💡 [핵심 안내]" -ForegroundColor Cyan
    Write-Host "  • 브라우저 우측 상단 패널에서 [🟢 ON / ⚪ OFF] 스위치를 직접 켜고 끌 수 있습니다." -ForegroundColor Gray
    Write-Host "  • 정각에 직접 누르거나 마우스 커서를 올려두지 마세요! 버튼이 열리면 0ms로 자동 클릭됩니다." -ForegroundColor Gray
    Write-Host ""

    $choice = Read-Host "  선택할 번호를 입력하세요 (기본값 1, 그냥 Enter 치면 즉시 실행)"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }

    if ($choice -eq "0") {
        Stop-Job $ServerJob -ErrorAction SilentlyContinue
        Remove-Job $ServerJob -Force -ErrorAction SilentlyContinue
        Write-Host "`n  BEOMCHRO를 종료합니다." -ForegroundColor Yellow
        break
    } elseif ($choice -eq "1") {
        if (-not $BrowserExe) {
            Write-Host "`n  ❌ Chrome, Edge 또는 Whale 브라우저를 찾을 수 없습니다!" -ForegroundColor Red
            Read-Host "  Enter를 누르면 돌아갑니다"
            continue
        }
        New-Item -ItemType Directory -Force -Path $ProfileDir | Out-Null
        $SimUrl = "http://localhost:$Port"
        $NolUrl = "https://nol.yanolja.com/ticket/genre/sports/postseason"

        Write-Host "`n  ⚡ 0ms 확장프로그램이 자동 장착된 전용 브라우저를 실행합니다..." -ForegroundColor Green
        Start-Process -FilePath $BrowserExe -ArgumentList @(
            "--load-extension=`"$ExtDir`"",
            "--user-data-dir=`"$ProfileDir`"",
            "--no-first-run",
            "--no-default-browser-check",
            $SimUrl,
            $NolUrl
        )
        Write-Host "  ✔ 브라우저가 실행되었습니다! 열린 창에서 [5초 카운트다운]으로 0ms 자동 격발을 테스트해 보세요." -ForegroundColor Cyan
        Read-Host "`n  메뉴로 돌아가려면 Enter를 누르세요 (연습장 서버 유지를 위해 이 창은 닫지 마세요)"
    }
}
