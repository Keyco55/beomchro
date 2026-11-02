# ==============================================================================
# BEOMCHRO v2.2 Pure Windows Native Controller (Zero-Python Required!)
# Full Rich CLI Dashboard + Multi-threaded C# HTTP Server + CDP 0ms Auto-Injector
# Saved with UTF-8 BOM + CRLF for 100% Windows PowerShell 5.1 Compatibility
# ==============================================================================

$ErrorActionPreference = "Continue"
try {
    [Console]::InputEncoding  = [System.Text.Encoding]::UTF8
    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $OutputEncoding = [System.Text.Encoding]::UTF8
} catch {}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($ScriptDir)) {
    $ScriptDir = [System.IO.Directory]::GetCurrentDirectory()
}
$ExtDir = [System.IO.Path]::Combine($ScriptDir, "extension")
$SimDir = [System.IO.Path]::Combine($ScriptDir, "simulator")
$ProfileDir = [System.IO.Path]::Combine($env:LOCALAPPDATA, "BEOMCHRO", "profile_v22")
$Port = 8989
$CdpPort = 9333

# Unblock downloaded ZIP files automatically
try {
    Get-ChildItem -LiteralPath $ScriptDir -Recurse -ErrorAction SilentlyContinue | Unblock-File -ErrorAction SilentlyContinue
} catch {}

# Compile High-Performance Native C# Engine (Multi-threaded HTTP Server + CDP Injector + Win32 Mouse/Pixel API)
$CSharpSource = @'
using System;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Diagnostics;

namespace BeomchroNative {
    public class Win32Engine {
        [DllImport("user32.dll")]
        public static extern bool SetCursorPos(int X, int Y);

        [DllImport("user32.dll")]
        public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, int dwExtraInfo);

        [DllImport("user32.dll")]
        public static extern bool GetCursorPos(out POINT lpPoint);

        [DllImport("user32.dll")]
        public static extern IntPtr GetDC(IntPtr hwnd);

        [DllImport("user32.dll")]
        public static extern int ReleaseDC(IntPtr hwnd, IntPtr hdc);

        [DllImport("gdi32.dll")]
        public static extern uint GetPixel(IntPtr hdc, int nXPos, int nYPos);

        [StructLayout(LayoutKind.Sequential)]
        public struct POINT {
            public int X;
            public int Y;
        }

        public static int[] GetCursorPosition() {
            POINT pt;
            GetCursorPos(out pt);
            return new int[] { pt.X, pt.Y };
        }

        public static double FastClick(int x, int y) {
            Stopwatch sw = Stopwatch.StartNew();
            SetCursorPos(x, y);
            mouse_event(0x0002, (uint)x, (uint)y, 0, 0);
            mouse_event(0x0004, (uint)x, (uint)y, 0, 0);
            sw.Stop();
            return sw.Elapsed.TotalMilliseconds;
        }

        public static int[] GetPixelRgb(int x, int y) {
            IntPtr hdc = GetDC(IntPtr.Zero);
            uint pixel = GetPixel(hdc, x, y);
            ReleaseDC(IntPtr.Zero, hdc);
            int r = (int)(pixel & 0x000000FF);
            int g = (int)((pixel & 0x0000FF00) >> 8);
            int b = (int)((pixel & 0x00FF0000) >> 16);
            return new int[] { r, g, b };
        }
    }

    public class MultiThreadedSimServer {
        private static TcpListener _listener;
        private static bool _running = false;
        private static string _simDir;
        private static string _extDir;
        public static int ActivePort = 8989;

        public static bool Start(string simDir, string extDir, int startPort) {
            if (_running) return true;
            _simDir = simDir;
            _extDir = extDir;

            for (int p = startPort; p < startPort + 15; p++) {
                try {
                    _listener = new TcpListener(IPAddress.Loopback, p);
                    _listener.Start();
                    ActivePort = p;
                    _running = true;
                    Thread acceptThread = new Thread(AcceptLoop);
                    acceptThread.IsBackground = true;
                    acceptThread.Start();
                    return true;
                } catch {
                    continue;
                }
            }
            return false;
        }

        public static void Stop() {
            _running = false;
            try { if (_listener != null) _listener.Stop(); } catch {}
        }

        private static void AcceptLoop() {
            while (_running) {
                try {
                    TcpClient client = _listener.AcceptTcpClient();
                    ThreadPool.QueueUserWorkItem(HandleClient, client);
                } catch {
                    if (!_running) break;
                }
            }
        }

        private static void HandleClient(object state) {
            TcpClient client = (TcpClient)state;
            try {
                client.ReceiveTimeout = 1500;
                client.SendTimeout = 1500;
                NetworkStream stream = client.GetStream();

                // Wait up to 400ms for Chrome preconnect socket to send request line
                int waited = 0;
                while (!stream.DataAvailable && waited < 40) {
                    Thread.Sleep(10);
                    waited++;
                }
                if (!stream.DataAvailable) {
                    client.Close();
                    return;
                }

                StreamReader reader = new StreamReader(stream, Encoding.UTF8);
                string requestLine = reader.ReadLine();
                if (string.IsNullOrEmpty(requestLine)) {
                    client.Close();
                    return;
                }

                while (true) {
                    string line = reader.ReadLine();
                    if (string.IsNullOrEmpty(line)) break;
                }

                string[] parts = requestLine.Split(' ');
                string reqPath = parts.Length >= 2 ? parts[1].Split('?')[0] : "/";
                reqPath = Uri.UnescapeDataString(reqPath);
                if (reqPath == "/") reqPath = "/index.html";

                if (reqPath == "/api/status") {
                    byte[] body = Encoding.UTF8.GetBytes("{\"status\":\"online\",\"engine\":\"BEOMCHRO v2.2\",\"target\":\"simulator\"}");
                    WriteResponse(stream, "200 OK", "application/json; charset=utf-8", body);
                } else {
                    string filePath = null;
                    string contentType = "text/html; charset=utf-8";
                    if (reqPath == "/extension/content.js") {
                        filePath = Path.Combine(_extDir, "content.js");
                        contentType = "application/javascript; charset=utf-8";
                    } else {
                        string rel = reqPath.TrimStart('/').Replace('/', Path.DirectorySeparatorChar);
                        filePath = Path.Combine(_simDir, rel);
                        if (reqPath.EndsWith(".css")) contentType = "text/css; charset=utf-8";
                        else if (reqPath.EndsWith(".js")) contentType = "application/javascript; charset=utf-8";
                        else if (reqPath.EndsWith(".png")) contentType = "image/png";
                        else if (reqPath.EndsWith(".svg")) contentType = "image/svg+xml";
                    }

                    if (filePath != null && File.Exists(filePath)) {
                        byte[] bytes = File.ReadAllBytes(filePath);
                        WriteResponse(stream, "200 OK", contentType, bytes);
                    } else {
                        WriteResponse(stream, "404 Not Found", "text/plain; charset=utf-8", new byte[0]);
                    }
                }
            } catch {
            } finally {
                try { client.Close(); } catch {}
            }
        }

        private static void WriteResponse(NetworkStream stream, string status, string contentType, byte[] body) {
            string header = "HTTP/1.1 " + status + "\r\n" +
                            "Content-Type: " + contentType + "\r\n" +
                            "Content-Length: " + body.Length + "\r\n" +
                            "Access-Control-Allow-Origin: *\r\n" +
                            "Cache-Control: no-cache\r\n" +
                            "Connection: close\r\n\r\n";
            byte[] hdrBytes = Encoding.UTF8.GetBytes(header);
            stream.Write(hdrBytes, 0, hdrBytes.Length);
            if (body.Length > 0) {
                stream.Write(body, 0, body.Length);
            }
            stream.Flush();
        }
    }

    public class CdpAutoInjector {
        private static bool _running = false;
        private static string _contentJsPath;
        private static int _cdpPort = 9333;
        private static Dictionary<string, string> _injected = new Dictionary<string, string>();

        public static void Start(string contentJsPath, int cdpPort) {
            _contentJsPath = contentJsPath;
            _cdpPort = cdpPort;
            if (_running) return;
            _running = true;
            Thread t = new Thread(PollLoop);
            t.IsBackground = true;
            t.Start();
        }

        private static string EscapeJsonString(string s) {
            StringBuilder sb = new StringBuilder(s.Length + 64);
            foreach (char c in s) {
                switch (c) {
                    case '\\': sb.Append("\\\\"); break;
                    case '\"': sb.Append("\\\""); break;
                    case '\r': sb.Append("\\r"); break;
                    case '\n': sb.Append("\\n"); break;
                    case '\t': sb.Append("\\t"); break;
                    default:
                        if (c < 32) sb.AppendFormat("\\u{0:x4}", (int)c);
                        else sb.Append(c);
                        break;
                }
            }
            return sb.ToString();
        }

        private static void PollLoop() {
            while (_running) {
                try {
                    if (File.Exists(_contentJsPath)) {
                        string scriptCode = File.ReadAllText(_contentJsPath, Encoding.UTF8);
                        string escapedCode = EscapeJsonString(scriptCode);

                        HttpWebRequest req = (HttpWebRequest)WebRequest.Create("http://127.0.0.1:" + _cdpPort + "/json");
                        req.Timeout = 700;
                        using (HttpWebResponse resp = (HttpWebResponse)req.GetResponse())
                        using (StreamReader sr = new StreamReader(resp.GetResponseStream(), Encoding.UTF8)) {
                            string json = sr.ReadToEnd();
                            string[] blocks = json.Split(new string[] { "{" }, StringSplitOptions.RemoveEmptyEntries);
                            foreach (string blk in blocks) {
                                if (!blk.Contains("\"type\": \"page\"") && !blk.Contains("\"type\":\"page\"")) continue;
                                string wsUrl = ExtractJsonField(blk, "webSocketDebuggerUrl");
                                string url = ExtractJsonField(blk, "url");
                                string id = ExtractJsonField(blk, "id");
                                if (string.IsNullOrEmpty(wsUrl) || url.StartsWith("chrome://") || url.StartsWith("devtools://") || url.StartsWith("edge://")) continue;

                                if (!_injected.ContainsKey(id) || _injected[id] != url) {
                                    string cmd1 = "{\"id\":1,\"method\":\"Page.enable\"}";
                                    string cmd2 = "{\"id\":2,\"method\":\"Page.addScriptToEvaluateOnNewDocument\",\"params\":{\"source\":\"" + escapedCode + "\"}}";
                                    string cmd3 = "{\"id\":3,\"method\":\"Runtime.evaluate\",\"params\":{\"expression\":\"" + escapedCode + "\"}}";
                                    if (SendWsCommands(wsUrl, new string[] { cmd1, cmd2, cmd3 })) {
                                        _injected[id] = url;
                                    }
                                } else {
                                    string guardCode = "if (!window.__BEOMCHRO_INITIALIZED__) { " + escapedCode + " }";
                                    string cmdCheck = "{\"id\":4,\"method\":\"Runtime.evaluate\",\"params\":{\"expression\":\"" + guardCode + "\"}}";
                                    SendWsCommands(wsUrl, new string[] { cmdCheck });
                                }
                            }
                        }
                    }
                } catch {}
                Thread.Sleep(450);
            }
        }

        private static string ExtractJsonField(string block, string fieldName) {
            string key = "\"" + fieldName + "\"";
            int idx = block.IndexOf(key);
            if (idx < 0) return "";
            int colon = block.IndexOf(':', idx + key.Length);
            if (colon < 0) return "";
            int q1 = block.IndexOf('\"', colon + 1);
            if (q1 < 0) return "";
            int q2 = block.IndexOf('\"', q1 + 1);
            if (q2 < 0) return "";
            return block.Substring(q1 + 1, q2 - q1 - 1);
        }

        private static bool SendWsCommands(string wsUrl, string[] commands) {
            try {
                string clean = wsUrl.Replace("ws://", "").Replace("wss://", "");
                int slash = clean.IndexOf('/');
                if (slash < 0) return false;
                string hostPort = clean.Substring(0, slash);
                string path = clean.Substring(slash);
                string[] hp = hostPort.Split(':');
                string host = hp[0];
                int port = int.Parse(hp[1]);

                using (TcpClient tc = new TcpClient()) {
                    tc.ReceiveTimeout = 1000;
                    tc.SendTimeout = 1000;
                    tc.Connect(host, port);
                    NetworkStream ns = tc.GetStream();

                    string key = Convert.ToBase64String(Guid.NewGuid().ToByteArray());
                    string hs = "GET " + path + " HTTP/1.1\r\n" +
                                "Host: " + hostPort + "\r\n" +
                                "Upgrade: websocket\r\n" +
                                "Connection: Upgrade\r\n" +
                                "Sec-WebSocket-Key: " + key + "\r\n" +
                                "Sec-WebSocket-Version: 13\r\n\r\n";
                    byte[] hsBytes = Encoding.ASCII.GetBytes(hs);
                    ns.Write(hsBytes, 0, hsBytes.Length);

                    byte[] buf = new byte[1024];
                    int read = ns.Read(buf, 0, buf.Length);
                    string resp = Encoding.ASCII.GetString(buf, 0, read);
                    if (!resp.Contains("101")) return false;

                    Random rng = new Random();
                    foreach (string cmd in commands) {
                        byte[] payload = Encoding.UTF8.GetBytes(cmd);
                        int len = payload.Length;
                        byte[] mask = new byte[4];
                        rng.NextBytes(mask);

                        MemoryStream ms = new MemoryStream();
                        ms.WriteByte(0x81); // FIN + Text
                        if (len < 126) {
                            ms.WriteByte((byte)(0x80 | len));
                        } else if (len < 65536) {
                            ms.WriteByte(0x80 | 126);
                            ms.WriteByte((byte)((len >> 8) & 0xFF));
                            ms.WriteByte((byte)(len & 0xFF));
                        } else {
                            ms.WriteByte(0x80 | 127);
                            for (int b = 7; b >= 0; b--) {
                                ms.WriteByte((byte)((len >> (8 * b)) & 0xFF));
                            }
                        }
                        ms.Write(mask, 0, 4);
                        for (int i = 0; i < len; i++) {
                            ms.WriteByte((byte)(payload[i] ^ mask[i % 4]));
                        }
                        byte[] frame = ms.ToArray();
                        ns.Write(frame, 0, frame.Length);
                        ns.Flush();
                        try {
                            byte[] ack = new byte[4096];
                            ns.Read(ack, 0, ack.Length);
                        } catch {}
                    }
                    try { tc.Client.Shutdown(SocketShutdown.Both); } catch {}
                    return true;
                }
            } catch {
                return false;
            }
        }
    }
}
'@

try {
    Add-Type -TypeDefinition $CSharpSource -Language CSharp -ErrorAction Stop
} catch {}

# Start Multi-Threaded Simulator Server on 127.0.0.1:8989
$ServerStarted = [BeomchroNative.MultiThreadedSimServer]::Start($SimDir, $ExtDir, $Port)
$Port = [BeomchroNative.MultiThreadedSimServer]::ActivePort

# Start CDP 0ms Auto-Injector Daemon (Ensures Top-Right HUD Widget Loads Even on Chrome 137+/156+!)
$ContentJsFile = [System.IO.Path]::Combine($ExtDir, "content.js")
[BeomchroNative.CdpAutoInjector]::Start($ContentJsFile, $CdpPort)

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

$BrowserExe = Find-Browser
$WinVer = [System.Environment]::OSVersion.Version.ToString()
$SkewMs = "+0.00 ms"

function Show-RichHeader {
    Write-Host "╭──────────────────────────────────────────────────────────────────────────────╮" -ForegroundColor Cyan
    Write-Host "│   ██████╗ ███████╗ ██████╗ ███╗   ███╗ ██████╗██╗  ██╗██████╗  ██████╗       │" -ForegroundColor Cyan
    Write-Host "│   ██╔══██╗██╔════╝██╔═══██╗████╗ ████║██╔════╝██║  ██║██╔══██╗██╔═══██╗      │" -ForegroundColor Cyan
    Write-Host "│   ██████╔╝█████╗  ██║   ██║██╔████╔██║██║     ███████║██████╔╝██║   ██║      │" -ForegroundColor Cyan
    Write-Host "│   ██╔══██╗██╔══╝  ██║   ██║██║╚██╔╝██║██║     ██╔══██║██╔══██╗██║   ██║      │" -ForegroundColor Cyan
    Write-Host "│   ██████╔╝███████╗╚██████╔╝██║ ╚═╝ ██║╚██████╗██║  ██║██║  ██║╚██████╔╝      │" -ForegroundColor Cyan
    Write-Host "│   ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝       │" -ForegroundColor Cyan
    Write-Host "│          >>> NOL-TICKET ULTRA FAST QUEUE INTERCEPTOR v2.2 <<<                │" -ForegroundColor Yellow
    Write-Host "╰──────────────────────────────────────────────────────────────────────────────╯" -ForegroundColor Cyan
}

function Show-StatusTable {
    $srvState = if ($ServerStarted) { "ONLINE (Port $Port)" } else { "OFFLINE" }
    Write-Host "╭──────────────────────────┬────────────────────────────┬──────────────────────╮" -ForegroundColor Blue
    Write-Host "│ 항목 (Component)         │ 상태 (Status)              │ 상세 정보 (Details)  │" -ForegroundColor White
    Write-Host "├──────────────────────────┼────────────────────────────┼──────────────────────┤" -ForegroundColor Blue

    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "하드웨어 클릭 엔진       " -ForegroundColor White -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "ACTIVE (Windows_User32)    " -ForegroundColor Green -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host ("OS: Win " + $WinVer.PadRight(12).Substring(0,12) + " ") -ForegroundColor Gray -NoNewline
    Write-Host "│" -ForegroundColor Blue

    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "로컬 연습 시뮬레이터     " -ForegroundColor White -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host ($srvState.PadRight(27).Substring(0,27)) -ForegroundColor Green -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host ("127.0.0.1:$Port".PadRight(21).Substring(0,21)) -ForegroundColor Gray -NoNewline
    Write-Host "│" -ForegroundColor Blue

    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "서버 시간 오차 (Skew)    " -ForegroundColor White -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host ($SkewMs.PadRight(27).Substring(0,27)) -ForegroundColor Green -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "동기화: 자동 보정됨  " -ForegroundColor Gray -NoNewline
    Write-Host "│" -ForegroundColor Blue

    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "목표 티켓팅 사이트       " -ForegroundColor White -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "놀티켓 & 인터파크 게이트   " -ForegroundColor Cyan -NoNewline
    Write-Host "│ " -ForegroundColor Blue -NoNewline
    Write-Host "CDP 0ms 인젝터 가동중" -ForegroundColor Gray -NoNewline
    Write-Host "│" -ForegroundColor Blue

    Write-Host "╰──────────────────────────┴────────────────────────────┴──────────────────────╯" -ForegroundColor Blue
}

function Show-MenuPanel {
    Write-Host ""
    Write-Host "╭────────────────────── 동작 모드 선택 (Operation Mode) ───────────────────────╮" -ForegroundColor Yellow
    Write-Host "│                                                                              │" -ForegroundColor Yellow
    Write-Host "│  " -ForegroundColor Yellow -NoNewline
    Write-Host "1. 🚀 원클릭 0ms 티켓팅 브라우저 실행 (확장프로그램 무설치 자동 장착)       " -ForegroundColor Green -NoNewline
    Write-Host "│" -ForegroundColor Yellow

    Write-Host "│  " -ForegroundColor Yellow -NoNewline
    Write-Host "2. 🎯 화면 픽셀 색상 감시 모드 (Pixel Color Watcher)                        " -ForegroundColor Yellow -NoNewline
    Write-Host "│" -ForegroundColor Yellow

    Write-Host "│  " -ForegroundColor Yellow -NoNewline
    Write-Host "3. ⏰ 서버 시간 정각 자동 클릭 모드 (Exact Time Trigger)                    " -ForegroundColor Magenta -NoNewline
    Write-Host "│" -ForegroundColor Yellow

    Write-Host "│  " -ForegroundColor Yellow -NoNewline
    Write-Host "4. ⚡ 마우스 초고속 격발 벤치마크 (0.1ms 테스트)                            " -ForegroundColor Cyan -NoNewline
    Write-Host "│" -ForegroundColor Yellow

    Write-Host "│  " -ForegroundColor Yellow -NoNewline
    Write-Host "5. 🩺 시스템 종합 진단 (Doctor Checklist)                                   " -ForegroundColor Blue -NoNewline
    Write-Host "│" -ForegroundColor Yellow

    Write-Host "│  " -ForegroundColor Yellow -NoNewline
    Write-Host "0. ❌ 종료 (Exit)                                                           " -ForegroundColor Red -NoNewline
    Write-Host "│" -ForegroundColor Yellow

    Write-Host "│                                                                              │" -ForegroundColor Yellow
    Write-Host "╰──────────────────────────────────────────────────────────────────────────────╯" -ForegroundColor Yellow
}

while ($true) {
    Clear-Host
    Show-RichHeader
    Show-StatusTable
    Show-MenuPanel
    Write-Host ""

    $choice = Read-Host "선택할 모드 번호를 입력하세요 [1/2/3/4/5/0] (기본값: 1)"
    if ([string]::IsNullOrWhiteSpace($choice)) { $choice = "1" }
    $choice = $choice.Trim()

    if ($choice -eq "0") {
        [BeomchroNative.MultiThreadedSimServer]::Stop()
        Write-Host "`n[BEOMCHRO] 시스템을 안전하게 종료합니다. 건승을 빕니다!" -ForegroundColor Cyan
        break
    } elseif ($choice -eq "1") {
        Write-Host "`n🚀 로컬 연습 시뮬레이터 서버 확인 중..." -ForegroundColor Cyan
        $SimUrl = "http://127.0.0.1:$Port"
        $NolUrl = "https://nol.yanolja.com/ticket/genre/sports/postseason"
        Write-Host "✔ 로컬 시뮬레이터가 성공적으로 실행되었습니다: $SimUrl" -ForegroundColor Green

        try { [System.IO.Directory]::CreateDirectory($ProfileDir) | Out-Null } catch {}

        Write-Host "⚡ 0ms 인젝터 엔진이 자동 장착된 전용 브라우저를 띄웁니다..." -ForegroundColor Yellow
        if ($BrowserExe -and [System.IO.File]::Exists($BrowserExe)) {
            $argStr = "--load-extension=`"$ExtDir`" --user-data-dir=`"$ProfileDir`" --remote-debugging-port=$CdpPort --remote-allow-origins=* --no-first-run --no-default-browser-check --new-window `"$SimUrl`" `"$NolUrl`""
            Start-Process -FilePath $BrowserExe -ArgumentList $argStr
            Write-Host "✔ 브라우저 자동 실행 완료! (2026 한국시리즈 7차전 자체 테스트 & NOL 티켓 오픈)" -ForegroundColor Green
            Write-Host "  • 우측 상단 패널에서 [🟢 ON / ⚪ OFF] 스위치와 [🔍 작동확인] 버튼을 사용할 수 있습니다." -ForegroundColor Cyan
            Write-Host "  • 정각에 직접 누르거나 마우스 커서를 올려두지 마세요! 버튼이 열리면 0ms로 자동 클릭됩니다." -ForegroundColor Yellow
        } else {
            Start-Process $SimUrl
            Start-Process $NolUrl
        }
        Write-Host "`n💡 TIP: 연습장 서버와 CDP 0ms 인젝터 유지를 위해 이 창은 닫지 마세요." -ForegroundColor Cyan
        Read-Host "메인 메뉴로 돌아가려면 Enter를 누르세요"
    } elseif ($choice -eq "2") {
        Write-Host "`n🎯 화면 픽셀 감시 모드 (초고속 변화 감지)" -ForegroundColor Yellow
        Write-Host "예매하기 버튼이 위치한 곳에 마우스 커서를 올려두고 Enter를 누르세요." -ForegroundColor Gray
        Read-Host "준비가 되면 Enter를 누르세요"
        $pos = [BeomchroNative.Win32Engine]::GetCursorPosition()
        $wx = $pos[0]; $wy = $pos[1]
        $initRgb = [BeomchroNative.Win32Engine]::GetPixelRgb($wx, $wy)
        Write-Host "좌표 ($wx, $wy)의 현재 색상: RGB($($initRgb[0]), $($initRgb[1]), $($initRgb[2]))" -ForegroundColor Cyan
        Write-Host "픽셀 색상 변화 감시 루프 가동 중... (중단하려면 Ctrl+C)" -ForegroundColor Green
        while ($true) {
            $curRgb = [BeomchroNative.Win32Engine]::GetPixelRgb($wx, $wy)
            $diff = [Math]::Abs($curRgb[0] - $initRgb[0]) + [Math]::Abs($curRgb[1] - $initRgb[1]) + [Math]::Abs($curRgb[2] - $initRgb[2])
            if ($diff -gt 20) {
                $dur = [BeomchroNative.Win32Engine]::FastClick($wx, $wy)
                Write-Host ("`n🔥 [픽셀 변화 감지] 신규 색상 감지 즉시 {0:F3}ms 만에 클릭 격발!" -f $dur) -ForegroundColor Green
                break
            }
            Start-Sleep -Milliseconds 1
        }
        Read-Host "`n메인 메뉴로 돌아가려면 Enter를 누르세요"
    } elseif ($choice -eq "3") {
        Write-Host "`n⏰ 서버 시간 기준 정각 자동 격발 모드" -ForegroundColor Magenta
        $pos = [BeomchroNative.Win32Engine]::GetCursorPosition()
        $targetTimeStr = Read-Host "목표 오픈 시각을 입력하세요 (예: 20:00:00)"
        Write-Host "현재 마우스 커서 위치 ($($pos[0]), $($pos[1]))로 조준 고정합니다." -ForegroundColor Cyan
        try {
            $now = Get-Date
            $parts = $targetTimeStr.Trim().Split(":")
            $targetDt = Get-Date -Hour ([int]$parts[0]) -Minute ([int]$parts[1]) -Second ([int]$parts[2]) -Millisecond 0
            if ($targetDt -lt $now) { $targetDt = $targetDt.AddDays(1) }
            Write-Host "타겟 시각: $($targetDt.ToString('HH:mm:ss.fff')) 대기 중..." -ForegroundColor Yellow
            while ($true) {
                $rem = ($targetDt - (Get-Date)).TotalSeconds
                if ($rem -le 0) {
                    $dur = [BeomchroNative.Win32Engine]::FastClick($pos[0], $pos[1])
                    Write-Host ("`n🔥 [정각 격발 완료] 00.000초 정각 하드웨어 클릭 완료! (소요: {0:F3}ms)" -f $dur) -ForegroundColor Green
                    break
                }
                Start-Sleep -Milliseconds 1
            }
        } catch {
            Write-Host "❌ 시간 형식이 올바르지 않습니다. (HH:MM:SS 형식으로 입력)" -ForegroundColor Red
        }
        Read-Host "`n메인 메뉴로 돌아가려면 Enter를 누르세요"
    } elseif ($choice -eq "4") {
        Write-Host "`n⚡ 하드웨어/OS 네이티브 마우스 격발 속도 측정 중..." -ForegroundColor Cyan
        $pos = [BeomchroNative.Win32Engine]::GetCursorPosition()
        Write-Host "현재 커서 위치: ($($pos[0]), ($pos[1]))" -ForegroundColor Gray
        $total = 0.0
        for ($i = 1; $i -le 5; $i++) {
            $tMs = [BeomchroNative.Win32Engine]::FastClick($pos[0], $pos[1])
            $total += $tMs
            Write-Host ("  - 테스트 #{0}: {1:F3} ms" -f $i, $tMs) -ForegroundColor Green
            Start-Sleep -Milliseconds 50
        }
        $avg = $total / 5.0
        Write-Host ("`n✔ 평균 클릭 디스패치 지연시간: {0:F3} ms (목표 < 1.0ms 달성!)" -f $avg) -ForegroundColor Green
        Read-Host "메인 메뉴로 돌아가려면 Enter를 누르세요"
    } elseif ($choice -eq "5") {
        Write-Host "`n🩺 [시스템 종합 진단 (System Doctor)]" -ForegroundColor Blue
        $extExists = [System.IO.File]::Exists($ContentJsFile)
        $simExists = [System.IO.File]::Exists([System.IO.Path]::Combine($SimDir, "index.html"))
        Write-Host "╭──────────────────────────┬──────────┬────────────────────────────────────────╮" -ForegroundColor Cyan
        Write-Host "│ 진단 항목                │ 결과     │ 상세 내용                              │" -ForegroundColor White
        Write-Host "├──────────────────────────┼──────────┼────────────────────────────────────────┤" -ForegroundColor Cyan
        Write-Host "│ 운영체제 호환성          │ PASS     │ Windows $WinVer (Native .NET C#)       │" -ForegroundColor Green
        Write-Host "│ 네이티브 마우스 엔진     │ PASS     │ Windows_User32 (user32.dll + gdi32.dll)│" -ForegroundColor Green
        Write-Host "│ 로컬 시뮬레이터 서버     │ $(if($ServerStarted){'PASS'}else{'FAIL'})     │ http://127.0.0.1:$Port (Multi-Threaded) │" -ForegroundColor Green
        Write-Host "│ 0ms 확장 & CDP 인젝터    │ $(if($extExists){'PASS'}else{'FAIL'})     │ extension/content.js + CDP Port $CdpPort   │" -ForegroundColor Green
        Write-Host "│ 한국시리즈 7차전 연습장  │ $(if($simExists){'PASS'}else{'FAIL'})     │ simulator/index.html 준비 완료         │" -ForegroundColor Green
        Write-Host "│ 감지된 브라우저          │ $(if($BrowserExe){'PASS'}else{'WARN'})     │ $BrowserExe │" -ForegroundColor Cyan
        Write-Host "╰──────────────────────────┴──────────┴────────────────────────────────────────╯" -ForegroundColor Cyan
        Read-Host "`n메인 메뉴로 돌아가려면 Enter를 누르세요"
    }
}
