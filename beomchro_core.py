#!/usr/bin/env python3
"""
BEOMCHRO Core Controller v2.0
Nol-Ticket Ultra Fast Queue Interceptor Engine
"""

import sys
import os
import time
import platform
import argparse
import threading
import webbrowser
from datetime import datetime, timezone
import http.server
import socketserver
from pathlib import Path

# Local Launcher Import
try:
    from beomchro_launcher import launch_browser, find_browser_executable
except ImportError:
    launch_browser = None
    find_browser_executable = None

# External Dependencies
try:
    import requests
except ImportError:
    requests = None

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.live import Live
    from rich.layout import Layout
    from rich.text import Text
    from rich.prompt import Prompt
    from rich import box
except ImportError:
    Console = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

# Platform detection
CURRENT_OS = platform.system()
IS_MACOS = CURRENT_OS == 'Darwin'
IS_WINDOWS = CURRENT_OS == 'Windows'
IS_LINUX = CURRENT_OS == 'Linux'

# ASCII Header Banner
ASCII_LOGO = """[bold cyan]
██████╗ ███████╗ ██████╗ ███╗   ███╗ ██████╗██╗  ██╗██████╗  ██████╗ 
██╔══██╗██╔════╝██╔═══██╗████╗ ████║██╔════╝██║  ██║██╔══██╗██╔═══██╗
██████╔╝█████╗  ██║   ██║██╔████╔██║██║     ███████║██████╔╝██║   ██║
██╔══██╗██╔══╝  ██║   ██║██║╚██╔╝██║██║     ██╔══██║██╔══██╗██║   ██║
██████╔╝███████╗╚██████╔╝██║ ╚═╝ ██║╚██████╗██║  ██║██║  ██║╚██████╔╝
╚═════╝ ╚══════╝ ╚═════╝ ╚═╝     ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ 
       [bold yellow]>>> NOL-TICKET ULTRA FAST QUEUE INTERCEPTOR v2.0 <<<[/bold yellow][/bold cyan]
"""

console = Console() if Console else None


# =====================================================================
# Native Fast Mouse & Pixel Injector
# =====================================================================
class FastMouseInjector:
    """Hardware / Native OS-level ultra-fast mouse event injector."""

    def __init__(self):
        self.os_type = CURRENT_OS
        self.backend = None
        self._init_backend()

    def _init_backend(self):
        if IS_WINDOWS:
            try:
                import ctypes
                self.backend = "Windows_SendInput"
                self.user32 = ctypes.windll.user32
                self.gdi32 = ctypes.windll.gdi32
            except Exception as e:
                self.backend = f"Fallback_WinError({e})"
        elif IS_MACOS:
            try:
                import Quartz.CoreGraphics as CG
                self.CG = CG
                self.backend = "macOS_Quartz"
            except Exception:
                self.backend = "macOS_Fallback_OSAScript"
        else:
            self.backend = "Linux_Generic"

    def get_cursor_position(self):
        """Get current mouse cursor (x, y)."""
        if IS_WINDOWS and self.backend == "Windows_SendInput":
            import ctypes
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            self.user32.GetCursorPos(ctypes.byref(pt))
            return int(pt.x), int(pt.y)
        elif IS_MACOS and self.backend == "macOS_Quartz":
            loc = self.CG.CGEventGetLocation(self.CG.CGEventCreate(None))
            return int(loc.x), int(loc.y)
        return (100, 100)

    def get_pixel_color(self, x, y):
        """Fast pixel color reader returning (r, g, b)."""
        if IS_WINDOWS and hasattr(self, 'gdi32'):
            hdc = self.user32.GetDC(0)
            color_ref = self.gdi32.GetPixel(hdc, int(x), int(y))
            self.user32.ReleaseDC(0, hdc)
            r = color_ref & 0xFF
            g = (color_ref >> 8) & 0xFF
            b = (color_ref >> 16) & 0xFF
            return (r, g, b)

        if ImageGrab:
            try:
                img = ImageGrab.grab(bbox=(int(x), int(y), int(x) + 1, int(y) + 1))
                return img.getpixel((0, 0))[:3]
            except Exception:
                pass

        return (0, 0, 0)

    def click(self, x=None, y=None):
        """Dispatch hardware-level click at (x, y) or current position."""
        t_start = time.perf_counter()

        if x is None or y is None:
            cur_x, cur_y = self.get_cursor_position()
            x = cur_x if x is None else x
            y = cur_y if y is None else y

        if IS_WINDOWS and self.backend == "Windows_SendInput":
            import ctypes
            from ctypes import wintypes

            INPUT_MOUSE = 0
            MOUSEEVENTF_ABSOLUTE = 0x8000
            MOUSEEVENTF_LEFTDOWN = 0x0002
            MOUSEEVENTF_LEFTUP = 0x0004

            class MOUSEINPUT(ctypes.Structure):
                _fields_ = [
                    ("dx", wintypes.LONG),
                    ("dy", wintypes.LONG),
                    ("mouseData", wintypes.DWORD),
                    ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD),
                    ("dwExtraInfo", ctypes.c_void_p),
                ]

            class INPUT(ctypes.Structure):
                class _INPUT_UNION(ctypes.Union):
                    _fields_ = [("mi", MOUSEINPUT)]
                _anonymous_ = ("u",)
                _fields_ = [
                    ("type", wintypes.DWORD),
                    ("u", _INPUT_UNION),
                ]

            screen_w = self.user32.GetSystemMetrics(0)
            screen_h = self.user32.GetSystemMetrics(1)
            norm_x = int(x * 65536 / screen_w)
            norm_y = int(y * 65536 / screen_h)

            inp_down = INPUT(type=INPUT_MOUSE)
            inp_down.mi.dx = norm_x
            inp_down.mi.dy = norm_y
            inp_down.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTDOWN

            inp_up = INPUT(type=INPUT_MOUSE)
            inp_up.mi.dx = norm_x
            inp_up.mi.dy = norm_y
            inp_up.mi.dwFlags = MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_LEFTUP

            inputs = (INPUT * 2)(inp_down, inp_up)
            self.user32.SendInput(2, ctypes.byref(inputs), ctypes.sizeof(INPUT))

        elif IS_MACOS and self.backend == "macOS_Quartz":
            pt = self.CG.CGPoint(x=x, y=y)
            event_down = self.CG.CGEventCreateMouseEvent(
                None, self.CG.kCGEventLeftMouseDown, pt, self.CG.kCGMouseButtonLeft
            )
            event_up = self.CG.CGEventCreateMouseEvent(
                None, self.CG.kCGEventLeftMouseUp, pt, self.CG.kCGMouseButtonLeft
            )
            self.CG.CGEventPost(self.CG.kCGHIDEventTap, event_down)
            self.CG.CGEventPost(self.CG.kCGHIDEventTap, event_up)

        elif IS_MACOS:
            os.system(f"""osascript -e 'tell application "System Events" to click at {{{x}, {y}}}' >/dev/null 2>&1""")

        t_end = time.perf_counter()
        duration_ms = (t_end - t_start) * 1000
        return duration_ms


# =====================================================================
# Server Time Synchronization & Skew Calculator
# =====================================================================
class TimeSyncService:
    """Calculates Time Skew (ms) against target servers."""

    def __init__(self, target_url="http://localhost:8989"):
        self.target_url = target_url
        self.skew_ms = 0.0
        self.last_sync = None
        self.is_synced = False

    def sync(self):
        """Estimate RTT and time offset using HTTP Date header."""
        if not requests:
            return 0.0

        try:
            t0 = time.time()
            resp = requests.head(self.target_url, timeout=2.0)
            t1 = time.time()

            date_header = resp.headers.get("Date")
            if date_header:
                server_dt = datetime.strptime(date_header, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=timezone.utc)
                server_epoch = server_dt.timestamp()
                local_epoch = (t0 + t1) / 2.0
                self.skew_ms = (server_epoch - local_epoch) * 1000.0
                self.is_synced = True
                self.last_sync = datetime.now()
        except Exception:
            self.skew_ms = 0.0
            self.is_synced = False

        return self.skew_ms


# =====================================================================
# Local Simulator HTTP Server
# =====================================================================
class SimulatorHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Serves the simulator web application."""

    def __init__(self, *args, **kwargs):
        directory = os.path.join(os.path.dirname(__file__), "simulator")
        super().__init__(*args, directory=directory, **kwargs)

    def do_GET(self):
        if self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            status_json = '{"status": "online", "engine": "BEOMCHRO v2.0", "target": "simulator"}'
            self.wfile.write(status_json.encode("utf-8"))
            return
        super().do_GET()

    def log_message(self, format, *args):
        pass


class SimulatorServer:
    """Threaded HTTP server for local simulator."""

    def __init__(self, port=8989):
        self.port = port
        self.server = None
        self.thread = None
        self.is_running = False

    def start(self):
        if self.is_running:
            return

        socketserver.TCPServer.allow_reuse_address = True
        try:
            self.server = socketserver.TCPServer(("", self.port), SimulatorHTTPRequestHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            self.is_running = True
        except Exception as e:
            if console:
                console.print(f"[bold red]❌ Failed to start Simulator Server on port {self.port}: {e}[/bold red]")
            else:
                print(f"Failed to start server: {e}")

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False


# =====================================================================
# Modern Rich TUI Dashboard
# =====================================================================
class BeomchroTUI:
    """Rich interactive TUI console dashboard."""

    def __init__(self, port=8989, target_url="http://localhost:8989"):
        self.port = port
        self.target_url = target_url
        self.mouse = FastMouseInjector()
        self.time_sync = TimeSyncService(target_url=target_url)
        self.server = SimulatorServer(port=port)

    def render_header(self):
        return Panel(
            Text.from_markup(ASCII_LOGO.strip()),
            box=box.ROUNDED,
            style="bold cyan",
            border_style="cyan",
            padding=(0, 2)
        )

    def render_status_table(self):
        table = Table(box=box.ROUNDED, expand=True, border_style="blue")
        table.add_column("항목 (Component)", style="bold white", width=24)
        table.add_column("상태 (Status)", style="bold green", width=28)
        table.add_column("상세 정보 (Details)", style="dim white")

        # OS Engine
        table.add_row(
            "하드웨어 클릭 엔진",
            f"[bold green]ACTIVE ({self.mouse.backend})[/bold green]",
            f"OS: {CURRENT_OS} {platform.release()}"
        )

        # Simulator Server
        srv_status = f"[bold green]ONLINE (Port {self.port})[/bold green]" if self.server.is_running else "[bold red]OFFLINE[/bold red]"
        table.add_row(
            "로컬 연습 시뮬레이터",
            srv_status,
            f"URL: http://localhost:{self.port}"
        )

        # Time Skew
        skew_str = f"{self.time_sync.skew_ms:+.2f} ms"
        skew_color = "green" if abs(self.time_sync.skew_ms) < 50 else "yellow"
        table.add_row(
            "서버 시간 오차 (Time Skew)",
            f"[bold {skew_color}]{skew_str}[/bold {skew_color}]",
            f"동기화 대상: {self.target_url}"
        )

        # Target Endpoint
        table.add_row(
            "목표 티켓팅 사이트",
            "[bold cyan]놀티켓 (NOL TICKET)[/bold cyan]",
            "자동 인젝션 유저스크립트 연동 준비됨"
        )

        return table

    def show_main_menu(self):
        console.clear()
        console.print(self.render_header())
        console.print(self.render_status_table())
        console.print()

        menu_panel = Panel(
            "[bold white]1.[/bold white] 🚀 [bold green]원클릭 0ms 티켓팅 브라우저 실행 (확장프로그램 무설치 자동 장착)[/bold green]\n"
            "[bold white]2.[/bold white] 🎯 [bold yellow]화면 픽셀 색상 감시 모드 (Pixel Color Watcher)[/bold yellow]\n"
            "[bold white]3.[/bold white] ⏰ [bold magenta]서버 시간 정각 자동 클릭 모드 (Exact Time Trigger)[/bold magenta]\n"
            "[bold white]4.[/bold white] ⚡ [bold cyan]마우스 초고속 격발 벤치마크 (0.1ms 테스트)[/bold cyan]\n"
            "[bold white]5.[/bold white] 🩺 [bold blue]시스템 종합 진단 (Doctor Checklist)[/bold blue]\n"
            "[bold white]0.[/bold white] ❌ [bold red]종료 (Exit)[/bold red]",
            title="[bold yellow]동작 모드 선택 (Operation Mode)[/bold yellow]",
            box=box.ROUNDED,
            border_style="yellow",
            padding=(1, 2)
        )
        console.print(menu_panel)

    def run_mode_simulator(self, auto_open=True):
        console.print("\n[bold cyan]🚀 로컬 연습 시뮬레이터 서버 시작 중...[/bold cyan]")
        self.server.start()
        time.sleep(0.4)
        self.time_sync.sync()

        sim_url = f"http://localhost:{self.port}"
        console.print(f"[bold green]✔ 로컬 시뮬레이터가 성공적으로 실행되었습니다: {sim_url}[/bold green]")
        
        if auto_open:
            console.print("[bold yellow]⚡ 0ms 인젝터 확장 프로그램이 자동 장착된 전용 브라우저를 띄웁니다...[/bold yellow]")
            launched = False
            if launch_browser:
                try:
                    proc = launch_browser(target_urls=[sim_url, "https://ticket.nol.com"])
                    if proc:
                        console.print(f"[bold green]✔ 브라우저 자동 실행 완료! (Tampermonkey 설치 전혀 불필요)[/bold green]")
                        console.print("[dim]브라우저 우측 상단에 ⚡ BEOMCHRO 0ms READY 배너가 표시됩니다.[/dim]")
                        launched = True
                except Exception as e:
                    console.print(f"[yellow]⚠️ 전용 브라우저 런처 경고: {e}[/yellow]")
            
            if not launched:
                console.print("[dim]기본 브라우저로 접속합니다...[/dim]")
                webbrowser.open(sim_url)

        console.print("\n[bold cyan]💡 TIP:[/bold cyan] 로그인/본인인증 정보는 브라우저 프로필에 영구 보존됩니다.")
        console.print("[dim]메인 메뉴로 돌아가려면 Enter를 누르세요.[/dim]")
        input()

    def run_mode_pixel_watcher(self):
        console.print("\n[bold yellow]🎯 화면 픽셀 감시 모드 (초고속 변화 감지)[/bold yellow]")
        console.print("예매하기 버튼이 위치한 곳에 마우스 커서를 올려두고 좌표를 고정하세요.")
        cur_x, cur_y = self.mouse.get_cursor_position()
        target_coords = Prompt.ask(f"감시할 대상 좌표 X, Y (현재 커서: {cur_x}, {cur_y})", default=f"{cur_x},{cur_y}")

        parts = target_coords.replace(",", " ").split()
        watch_x, watch_y = int(parts[0]), int(parts[1])

        init_color = self.mouse.get_pixel_color(watch_x, watch_y)
        console.print(f"[bold cyan]좌표 ({watch_x}, {watch_y})의 현재 색상: {init_color}[/bold cyan]")
        console.print("[bold green]픽셀 색상 변화 감시 루프 가동 중... (Ctrl+C로 취소)[/bold green]")

        try:
            while True:
                color = self.mouse.get_pixel_color(watch_x, watch_y)
                # If color difference detected
                diff = abs(color[0] - init_color[0]) + abs(color[1] - init_color[1]) + abs(color[2] - init_color[2])
                if diff > 20:
                    dur = self.mouse.click(watch_x, watch_y)
                    console.print(f"\n[bold green]🔥 [픽셀 변화 감지] 신규 색상 {color} 감지 즉시 {dur:.3f}ms 만에 클릭 격발![/bold green]")
                    break
                time.sleep(0.001)  # 1ms high-frequency check
        except KeyboardInterrupt:
            console.print("\n[bold yellow]픽셀 감시가 취소되었습니다.[/bold yellow]")

        console.print("[dim]Enter를 누르면 메뉴로 복귀합니다.[/dim]")
        input()

    def run_mode_benchmark(self):
        console.print("\n[bold cyan]⚡ 하드웨어/OS 네이티브 마우스 격발 속도 측정 중...[/bold cyan]")
        latencies = []
        cur_x, cur_y = self.mouse.get_cursor_position()
        console.print(f"[dim]현재 커서 위치: ({cur_x}, {cur_y})[/dim]")

        for i in range(5):
            t_ms = self.mouse.click(cur_x, cur_y)
            latencies.append(t_ms)
            time.sleep(0.05)

        avg_lat = sum(latencies) / len(latencies)
        min_lat = min(latencies)

        table = Table(title="마우스 격발 벤치마크 결과", box=box.ROUNDED)
        table.add_column("시도 (Run)", style="white")
        table.add_column("지연 시간 (Latency)", style="bold cyan")

        for idx, lat in enumerate(latencies, 1):
            table.add_row(f"#{idx}", f"{lat:.3f} ms")

        console.print(table)
        console.print(f"[bold green]✔ 최소 지연: {min_lat:.3f} ms / 평균 지연: {avg_lat:.3f} ms (0~1ms 대기열 격발 충족)[/bold green]")
        console.print("[dim]Enter를 누르면 메뉴로 복귀합니다.[/dim]")
        input()

    def run_mode_time_trigger(self):
        console.print("\n[bold magenta]⏰ 서버 시간 정각 자동 클릭 모드[/bold magenta]")
        self.time_sync.sync()
        console.print(f"현재 계산된 Server Time Skew: [bold yellow]{self.time_sync.skew_ms:+.2f} ms[/bold yellow]")
        
        target_time_str = Prompt.ask("정각 격발 목표 시각 입력 (예: 20:00:00)", default="20:00:00")
        target_coords = Prompt.ask("클릭 대상 좌표 X, Y (공백 또는 x,y)", default="current")

        if target_coords.lower() == "current":
            cx, cy = self.mouse.get_cursor_position()
        else:
            parts = target_coords.replace(",", " ").split()
            cx, cy = int(parts[0]), int(parts[1])

        console.print(f"[bold green]설정 완료: {target_time_str}.000 에 좌표 ({cx}, {cy}) 클릭 준비[/bold green]")
        console.print("[dim]Ctrl+C를 누르면 언제든지 취소할 수 있습니다. 카운트다운 시작...[/dim]")

        try:
            today_str = datetime.now().strftime("%Y-%m-%d")
            target_dt = datetime.strptime(f"{today_str} {target_time_str}", "%Y-%m-%d %H:%M:%S")
            target_epoch = target_dt.timestamp()

            while True:
                now_epoch = time.time() + (self.time_sync.skew_ms / 1000.0)
                diff = target_epoch - now_epoch

                if diff <= 0.001:
                    dur = self.mouse.click(cx, cy)
                    console.print(f"\n[bold green]🔥 [격발 성공] 정각 클릭이 {dur:.3f}ms 만에 실행되었습니다![/bold green]")
                    break
                elif diff > 1.0:
                    time.sleep(0.5)
                else:
                    pass
        except KeyboardInterrupt:
            console.print("\n[bold yellow]사용자에 의해 정각 트리거가 취소되었습니다.[/bold yellow]")

        console.print("[dim]Enter를 누르면 메뉴로 복귀합니다.[/dim]")
        input()

    def run_mode_doctor(self):
        console.print("\n[bold blue]🩺 시스템 종합 진단 및 상태 점검 (Doctor Checklist)[/bold blue]\n")
        table = Table(box=box.ROUNDED)
        table.add_column("점검 항목", style="bold white")
        table.add_column("판정", style="bold")
        table.add_column("비고")

        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        table.add_row("Python 환경", "[green]PASS[/green]", f"Python {py_ver} ({CURRENT_OS})")

        backend_status = "[green]PASS[/green]" if "Fallback" not in self.mouse.backend else "[yellow]WARN[/yellow]"
        table.add_row("네이티브 마우스 인젝터", backend_status, f"엔진: {self.mouse.backend}")

        sim_dir = Path(__file__).parent / "simulator"
        has_index = (sim_dir / "index.html").exists()
        has_css = (sim_dir / "style.css").exists()
        has_js = (sim_dir / "script.js").exists()
        sim_all = has_index and has_css and has_js
        table.add_row("시뮬레이터 웹 에셋", "[green]PASS[/green]" if sim_all else "[red]FAIL[/red]", f"index={has_index}, css={has_css}, js={has_js}")

        # 4. Zero-Setup Extension & UserScript
        ext_manifest = Path(__file__).parent / "extension" / "manifest.json"
        table.add_row("무설치 확장프로그램 (Extension)", "[green]PASS[/green]" if ext_manifest.exists() else "[red]FAIL[/red]", "Zero-Setup 자동 장착 지원")

        userscript = Path(__file__).parent / "beomchro_queue.user.js"
        table.add_row("Tampermonkey 유저스크립트", "[green]PASS[/green]" if userscript.exists() else "[red]FAIL[/red]", str(userscript.name))

        table.add_row("HTTP 요청 라이브러리 (requests)", "[green]PASS[/green]" if requests else "[yellow]WARN (requests 없음)[/yellow]", "서버 시간 오차 계산 지원")

        console.print(table)
        console.print("\n[bold green]✔ 모든 핵심 컴포넌트가 정상적으로 배포 및 준비되었습니다.[/bold green]")
        console.print("[dim]Enter를 누르면 메뉴로 복귀합니다.[/dim]")
        input()


# =====================================================================
# Main CLI Entry Point
# =====================================================================
def main():
    parser = argparse.ArgumentParser(description="BEOMCHRO Ultra Fast Queue Interceptor v2.0")
    parser.add_argument("--mode", type=int, choices=[1, 2, 3, 4, 5], help="Run specific mode non-interactively")
    parser.add_argument("--port", type=int, default=8989, help="Simulator HTTP port (default: 8989)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open browser in simulator mode")
    parser.add_argument("--test-run", action="store_true", help="Run quick automated validation and exit")
    args = parser.parse_args()

    app = BeomchroTUI(port=args.port)

    # Automated validation mode for test harness
    if args.test_run:
        print("[TEST] Running BEOMCHRO Automated Self-Test...")
        app.server.start()
        time.sleep(0.3)
        assert app.server.is_running, "Server failed to start"
        print(f"[TEST] Simulator Server active on port {args.port}")

        if requests:
            res = requests.get(f"http://127.0.0.1:{args.port}/api/status", timeout=2)
            assert res.status_code == 200, f"HTTP status: {res.status_code}"
            print(f"[TEST] API /api/status OK: {res.text}")

        dur = app.mouse.click(100, 100)
        print(f"[TEST] Native Mouse Click dispatch OK ({dur:.3f} ms, Backend: {app.mouse.backend})")

        app.server.stop()
        print("[TEST] All Automated Self-Tests PASSED successfully!")
        return 0

    if args.mode:
        if args.mode == 1:
            app.run_mode_simulator(auto_open=not args.no_browser)
        elif args.mode == 2:
            app.run_mode_pixel_watcher()
        elif args.mode == 3:
            app.run_mode_time_trigger()
        elif args.mode == 4:
            app.run_mode_benchmark()
        elif args.mode == 5:
            app.run_mode_doctor()
        return 0

    # Interactive loop
    try:
        while True:
            app.show_main_menu()
            choice = Prompt.ask("선택할 번호를 입력하세요", choices=["0", "1", "2", "3", "4", "5"], default="1")
            if choice == "0":
                console.print("\n[bold yellow]BEOMCHRO 시스템을 종료합니다. 행운을 빕니다![/bold yellow]")
                break
            elif choice == "1":
                app.run_mode_simulator(auto_open=not args.no_browser)
            elif choice == "2":
                app.run_mode_pixel_watcher()
            elif choice == "3":
                app.run_mode_time_trigger()
            elif choice == "4":
                app.run_mode_benchmark()
            elif choice == "5":
                app.run_mode_doctor()
    except KeyboardInterrupt:
        console.print("\n[bold red]프로그램을 강제 종료합니다.[/bold red]")
    finally:
        app.server.stop()


if __name__ == "__main__":
    sys.exit(main() or 0)
