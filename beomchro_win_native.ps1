# ==============================================================================
# BEOMCHRO v2.1 Pure Windows Native Controller (Zero-Python Required!)
# Saved with UTF-8 BOM + CRLF for 100% Windows PowerShell 5.1 Compatibility
# ==============================================================================

$ErrorActionPreference = "Continue"
try {
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($ScriptDir)) { $ScriptDir = [System.IO.Directory]::GetCurrentDirectory() }
$ExtDir = [System.IO.Path]::Combine($ScriptDir, "extension")
$SimDir = [System.IO.Path]::Combine($ScriptDir, "simulator")
$ProfileDir = [System.IO.Path]::Combine($env:LOCALAPPDATA, "BEOMCHRO", "browser_profile")
$Port = 8989

# Unblock Zone.Identifier (Mark of the Web) on downloaded ZIP files
try {
    Get-ChildItem -LiteralPath $ScriptDir -Recurse -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue
} catch {}

function Find-Browser {
    $regKeys = @(
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\whale.exe",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\whale.exe",
        "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe",
        "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"
    )
    foreach ($rk in $regKeys) {
        try {
            $val = (Get-ItemProperty -Path $rk -ErrorAction SilentlyContinue)."(default)"
            if ($val -and [System.IO.File]::Exists($val)) { return $val }
        } catch {}
    }
    $paths = @(
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
        "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe",
        "$env:ProgramFiles\Naver\Naver Whale\Application\whale.exe",
        "$env:LOCALAPPDATA\Naver\Naver Whale\Application\whale.exe",
        "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "$env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe"
    )
    foreach ($p in $paths) {
        if ($p -and [System.IO.File]::Exists($p)) { return $p }
    }
    return $null
}

# Start In-Process Background HTTP Server on 127.0.0.1:8989
try {
    $ServerRunspace = [runspacefactory]::CreateRunspace()
    $ServerRunspace.Open()
    $ServerPS = [powershell]::Create()
    $ServerPS.Runspace = $ServerRunspace
    [void]$ServerPS.AddScript({
        param($SimDir, $ExtDir, $Port)
        try {
            $listener = New-Object System.Net.Sockets.TcpListener([System.Net.IPAddress]::Loopback, $Port)
            $listener.Start()
            while ($true) {
                $client = $listener.AcceptTcpClient()
                try {
                    $stream = $client.GetStream()
                    $reader = New-Object System.IO.StreamReader($stream)
                    $requestLine = $reader.ReadLine()
                    if ($requestLine) {
                        while ($true) {
                            $line = $reader.ReadLine()
                            if ($null -eq $line -or $line -eq "") { break }
                        }
                        $parts = $requestLine.Split(" ")
                        $reqPath = if ($parts.Length -ge 2) { $parts[1].Split("?")[0] } else { "/" }
                        $reqPath = [System.Uri]::UnescapeDataString($reqPath)
                        if ($reqPath -eq "/") { $reqPath = "/index.html" }

                        if ($reqPath -eq "/api/status") {
                            $jsonBytes = [System.Text.Encoding]::UTF8.GetBytes('{"status":"online","engine":"BEOMCHRO v2.1","target":"simulator"}')
                            $hdr = "HTTP/1.1 200 OK`r`nContent-Type: application/json; charset=utf-8`r`nContent-Length: $($jsonBytes.Length)`r`nAccess-Control-Allow-Origin: *`r`nConnection: close`r`n`r`n"
                            $hdrBytes = [System.Text.Encoding]::UTF8.GetBytes($hdr)
                            $stream.Write($hdrBytes, 0, $hdrBytes.Length)
                            $stream.Write($jsonBytes, 0, $jsonBytes.Length)
                        } else {
                            $filePath = $null
                            $contentType = "text/html; charset=utf-8"
                            if ($reqPath -eq "/extension/content.js") {
                                $filePath = [System.IO.Path]::Combine($ExtDir, "content.js")
                                $contentType = "application/javascript; charset=utf-8"
                            } else {
                                $relPath = $reqPath.TrimStart("/").Replace("/", "\")
                                $filePath = [System.IO.Path]::Combine($SimDir, $relPath)
                                if ($reqPath.EndsWith(".css")) { $contentType = "text/css; charset=utf-8" }
                                elseif ($reqPath.EndsWith(".js")) { $contentType = "application/javascript; charset=utf-8" }
                            }
                            if ($filePath -and [System.IO.File]::Exists($filePath)) {
                                $bytes = [System.IO.File]::ReadAllBytes($filePath)
                                $hdr = "HTTP/1.1 200 OK`r`nContent-Type: $contentType`r`nContent-Length: $($bytes.Length)`r`nAccess-Control-Allow-Origin: *`r`nConnection: close`r`n`r`n"
                                $hdrBytes = [System.Text.Encoding]::UTF8.GetBytes($hdr)
                                $stream.Write($hdrBytes, 0, $hdrBytes.Length)
                                $stream.Write($bytes, 0, $bytes.Length)
                            } else {
                                $nf = [System.Text.Encoding]::UTF8.GetBytes("HTTP/1.1 404 Not Found`r`nContent-Length: 0`r`nConnection: close`r`n`r`n")
                                $stream.Write($nf, 0, $nf.Length)
                            }
                        }
                    }
                } catch {} finally {
                    $client.Close()
                }
            }
        } catch {}
    }).AddArgument($SimDir).AddArgument($ExtDir).AddArgument($Port)
    $ServerHandle = $ServerPS.BeginInvoke()
    Start-Sleep -Milliseconds 250
} catch {}

$BrowserExe = Find-Browser

while ($true) {
    Clear-Host
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host "   [BEOMCHRO v2.1] NOL-TICKET & INTERPARK 0ms QUEUE INTERCEPTOR (WIN)    " -ForegroundColor Yellow
    Write-Host "==========================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  [시스템 상태]" -ForegroundColor White
    Write-Host "  * 실행 엔진        : ACTIVE (Windows 무설치 내장 엔진 - 파이썬 불필요)" -ForegroundColor Green
    Write-Host "  * 자체 테스트 서버 : ONLINE (http://localhost:$Port)" -ForegroundColor Green
    if ($BrowserExe) {
        Write-Host "  * 감지된 브라우저  : $BrowserExe" -ForegroundColor Cyan
    } else {
        Write-Host "  * 감지된 브라우저  : 기본 브라우저 모드로 실행됩니다" -ForegroundColor Yellow
    }
    Write-Host ""
    Write-Host "  [동작 모드 선택]" -ForegroundColor Yellow
    Write-Host "  1. [추천] 원클릭 0ms 티켓팅 브라우저 & 2026 한국시리즈 7차전 연습장 실행" -ForegroundColor Green
    Write-Host "  0. 프로그램 종료 (Exit)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  [필독 안내]" -ForegroundColor Cyan
    Write-Host "  * 브라우저 우측 상단 위젯에서 [ON (작동중) / OFF (정지됨)] 스위치를 조작할 수 있습니다." -ForegroundColor Gray
    Write-Host "  * 정각에 직접 누르거나 마우스 커서를 올려두지 마세요! (손을 떼고 있으면 0ms 자동 클릭)" -ForegroundColor Gray
    Write-Host ""

    $choice = Read-Host "  선택할 번호를 입력 후 Enter를 누르세요 (그냥 Enter 치면 1번 즉시 실행)"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }
    $choice = $choice.Trim()

    if ($choice -eq "0") {
        try { $ServerPS.Dispose(); $ServerRunspace.Close() } catch {}
        Write-Host "`n  프로그램을 종료합니다." -ForegroundColor Yellow
        break
    } elseif ($choice -eq "1") {
        try { [System.IO.Directory]::CreateDirectory($ProfileDir) | Out-Null } catch {}
        $SimUrl = "http://localhost:$Port"
        $NolUrl = "https://nol.yanolja.com/ticket/genre/sports/postseason"

        Write-Host "`n  [실행 중] 0ms 확장프로그램이 자동 장착된 전용 브라우저를 엽니다..." -ForegroundColor Green
        if ($BrowserExe -and [System.IO.File]::Exists($BrowserExe)) {
            $argStr = "--load-extension=`"$ExtDir`" --user-data-dir=`"$ProfileDir`" --no-first-run --no-default-browser-check `"$SimUrl`" `"$NolUrl`""
            Start-Process -FilePath $BrowserExe -ArgumentList $argStr
        } else {
            Start-Process $SimUrl
            Start-Process $NolUrl
        }
        Write-Host "  [완료] 브라우저가 열렸습니다!" -ForegroundColor Cyan
        Write-Host "  * 연습장 상단의 [5초 카운트다운] 버튼을 누르고 마우스에서 손을 떼고 테스트해 보세요." -ForegroundColor Yellow
        Write-Host "  * 주의: 연습장 서버 유지를 위해 이 검은색 창은 닫지 마세요!" -ForegroundColor Red
        Read-Host "`n  메뉴 화면으로 돌아가려면 Enter를 누르세요"
    }
}
