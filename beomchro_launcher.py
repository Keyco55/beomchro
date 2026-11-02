#!/usr/bin/env python3
"""
BEOMCHRO Browser Launcher v2.2
Detects installed browsers, launches a dedicated session, and runs a zero-dependency
CDP (Chrome DevTools Protocol) background injector so Chrome 137+/156+ (which ignores
--load-extension) still auto-injects extension/content.js into every tab in 0ms.
"""

import sys
import os
import time
import json
import base64
import socket
import struct
import threading
import platform
import subprocess
import urllib.request
from pathlib import Path

CURRENT_OS = platform.system()
IS_MACOS = CURRENT_OS == 'Darwin'
IS_WINDOWS = CURRENT_OS == 'Windows'
IS_LINUX = CURRENT_OS == 'Linux'

PROJECT_DIR = Path(__file__).resolve().parent
EXTENSION_DIR = PROJECT_DIR / "extension"
USER_DATA_DIR = Path.home() / ".beomchro" / "profile_v22"
CDP_PORT = 9333

_cdp_thread = None
_cdp_stop_event = threading.Event()


def find_browser_executable():
    """Detect installed Chromium-based browser executable path."""
    candidates = []

    if IS_MACOS:
        candidates = [
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path.home() / "Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            Path("/Applications/Naver Whale.app/Contents/MacOS/Naver Whale"),
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            Path("/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"),
            Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
        ]
    elif IS_WINDOWS:
        local_app = os.environ.get("LOCALAPPDATA", "")
        prog_files = os.environ.get("ProgramFiles", "C:\\Program Files")
        prog_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")

        candidates = [
            Path(prog_files) / "Google/Chrome/Application/chrome.exe",
            Path(prog_files_x86) / "Google/Chrome/Application/chrome.exe",
            Path(local_app) / "Google/Chrome/Application/chrome.exe",
            Path(prog_files) / "Microsoft/Edge/Application/msedge.exe",
            Path(prog_files_x86) / "Microsoft/Edge/Application/msedge.exe",
            Path(prog_files) / "Naver/Naver Whale/Application/whale.exe",
            Path(local_app) / "Naver/Naver Whale/Application/whale.exe",
            Path(prog_files) / "BraveSoftware/Brave-Browser/Application/brave.exe",
        ]
    else:
        candidates = [
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/google-chrome-stable"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
        ]

    for p in candidates:
        if p.exists() and os.access(str(p), os.X_OK if not IS_WINDOWS else os.F_OK):
            return p

    for name in ["google-chrome", "chrome", "msedge", "whale", "chromium"]:
        found = subprocess.run(["which" if not IS_WINDOWS else "where", name], capture_output=True, text=True)
        if found.returncode == 0 and found.stdout.strip():
            first_line = found.stdout.strip().splitlines()[0]
            if Path(first_line).exists():
                return Path(first_line)

    return None


def _ws_send_cdp_commands(ws_url: str, commands: list):
    """Minimal RFC 6455 WebSocket client using only Python stdlib socket to send CDP JSON commands."""
    try:
        # Parse ws://127.0.0.1:9333/devtools/page/XXXX
        without_scheme = ws_url.replace("ws://", "").replace("wss://", "")
        host_port, path = without_scheme.split("/", 1)
        path = "/" + path
        if ":" in host_port:
            host, port_str = host_port.split(":", 1)
            port = int(port_str)
        else:
            host, port = host_port, 80

        sock = socket.create_connection((host, port), timeout=1.5)
        try:
            key = base64.b64encode(os.urandom(16)).decode("ascii")
            handshake = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {host}:{port}\r\n"
                f"Upgrade: websocket\r\n"
                f"Connection: Upgrade\r\n"
                f"Sec-WebSocket-Key: {key}\r\n"
                f"Sec-WebSocket-Version: 13\r\n\r\n"
            )
            sock.sendall(handshake.encode("ascii"))

            resp = b""
            while b"\r\n\r\n" not in resp:
                chunk = sock.recv(1024)
                if not chunk:
                    return False
                resp += chunk

            if b"101" not in resp.splitlines()[0]:
                return False

            for cmd in commands:
                payload = json.dumps(cmd).encode("utf-8")
                length = len(payload)
                mask_key = os.urandom(4)

                header = bytearray([0x81])  # FIN + text frame
                if length < 126:
                    header.append(0x80 | length)
                elif length < 65536:
                    header.append(0x80 | 126)
                    header.extend(struct.pack("!H", length))
                else:
                    header.append(0x80 | 127)
                    header.extend(struct.pack("!Q", length))

                header.extend(mask_key)
                masked_payload = bytearray(length)
                for i in range(length):
                    masked_payload[i] = payload[i] ^ mask_key[i % 4]

                sock.sendall(header + masked_payload)
                # Wait for Chrome CDP acknowledgment frame so Winsock/macOS never resets the socket early
                try:
                    sock.recv(4096)
                except Exception:
                    pass

            try:
                sock.shutdown(socket.SHUT_WR)
            except Exception:
                pass
            return True
        finally:
            sock.close()
    except Exception:
        return False


def start_cdp_injector_daemon(ext_dir: Path, cdp_port: int = CDP_PORT):
    """
    Background daemon that polls Chrome DevTools Protocol (127.0.0.1:9333/json)
    and injects extension/content.js into every open tab & new navigation.
    Solves Chrome 137+/156+ ignoring --load-extension!
    """
    global _cdp_thread
    if _cdp_thread and _cdp_thread.is_alive():
        return

    content_js_path = ext_dir / "content.js"
    if not content_js_path.exists():
        return

    def _worker():
        injected_targets = {}
        while not _cdp_stop_event.is_set():
            try:
                script_code = content_js_path.read_text(encoding="utf-8")
                req = urllib.request.Request(
                    f"http://127.0.0.1:{cdp_port}/json",
                    headers={"User-Agent": "BEOMCHRO-CDP/2.2"}
                )
                with urllib.request.urlopen(req, timeout=0.8) as resp:
                    targets = json.loads(resp.read().decode("utf-8"))

                for t in targets:
                    if t.get("type") != "page":
                        continue
                    target_id = t.get("id", "")
                    url = t.get("url", "")
                    ws_url = t.get("webSocketDebuggerUrl", "")
                    if not ws_url or url.startswith("devtools://") or url.startswith("chrome://"):
                        continue

                    # Re-evaluate if URL changed or not yet injected
                    if injected_targets.get(target_id) != url:
                        cmds = [
                            {"id": 1, "method": "Page.enable"},
                            {
                                "id": 2,
                                "method": "Page.addScriptToEvaluateOnNewDocument",
                                "params": {"source": script_code}
                            },
                            {
                                "id": 3,
                                "method": "Runtime.evaluate",
                                "params": {"expression": script_code}
                            }
                        ]
                        if _ws_send_cdp_commands(ws_url, cmds):
                            injected_targets[target_id] = url
                    else:
                        # Periodic lightweight check in case page reloaded same URL
                        cmds = [
                            {
                                "id": 4,
                                "method": "Runtime.evaluate",
                                "params": {"expression": "if (!window.__BEOMCHRO_INITIALIZED__) { " + script_code + " }"}
                            }
                        ]
                        _ws_send_cdp_commands(ws_url, cmds)
            except Exception:
                pass
            time.sleep(0.5)

    _cdp_thread = threading.Thread(target=_worker, daemon=True)
    _cdp_thread.start()


def launch_browser(target_urls=None, extension_path=None, profile_dir=None, dry_run=False):
    """Launch dedicated browser instance with auto-loaded extension and CDP 0ms injector."""
    browser_exe = find_browser_executable()
    if not browser_exe:
        raise RuntimeError("크롬(Google Chrome), 웨일(Whale), 또는 엣지(Edge) 브라우저를 찾을 수 없습니다. 브라우저 설치를 확인해주세요.")

    ext_dir = Path(extension_path) if extension_path else EXTENSION_DIR
    data_dir = Path(profile_dir) if profile_dir else USER_DATA_DIR

    if not ext_dir.exists():
        raise FileNotFoundError(f"확장 프로그램 디렉터리가 존재하지 않습니다: {ext_dir}")

    if not dry_run:
        try:
            data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            data_dir = PROJECT_DIR / ".browser_profile_v22"
            data_dir.mkdir(parents=True, exist_ok=True)

        # If CDP port 9333 is not listening, ensure no stale lock blocks new window creation
        cdp_alive = False
        try:
            with socket.create_connection(("127.0.0.1", CDP_PORT), timeout=0.25):
                cdp_alive = True
        except Exception:
            cdp_alive = False

        if not cdp_alive:
            for lock_name in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
                lock_file = data_dir / lock_name
                if lock_file.exists() or lock_file.is_symlink():
                    try:
                        lock_file.unlink()
                    except Exception:
                        pass

    if not target_urls:
        target_urls = ["http://127.0.0.1:8989"]

    args = [
        str(browser_exe),
        f"--load-extension={ext_dir.resolve()}",
        f"--user-data-dir={data_dir.resolve()}",
        f"--remote-debugging-port={CDP_PORT}",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        "--new-window",
    ] + list(target_urls)

    if dry_run:
        print("[DRY-RUN] Browser Executable:", browser_exe)
        print("[DRY-RUN] Extension Path:", ext_dir)
        print("[DRY-RUN] Profile Dir:", data_dir)
        print("[DRY-RUN] Command:", " ".join(f'"{a}"' if " " in a else a for a in args))
        return None

    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    start_cdp_injector_daemon(ext_dir=ext_dir.resolve(), cdp_port=CDP_PORT)
    return proc


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BEOMCHRO Browser Launcher")
    parser.add_argument("--dry-run", action="store_true", help="Print command without launching")
    parser.add_argument("--url", nargs="*", default=["http://127.0.0.1:8989"], help="URLs to open")
    args = parser.parse_args()

    try:
        browser = find_browser_executable()
        if args.dry_run:
            print(f"✔ 감지된 브라우저: {browser}")
            launch_browser(target_urls=args.url, dry_run=True)
            print("✔ 드라이런 검증 성공!")
            return 0

        print(f"🚀 티켓팅 전용 브라우저 실행 중 ({browser})...")
        proc = launch_browser(target_urls=args.url)
        print(f"✔ 브라우저가 실행되었습니다 (PID: {proc.pid})")
        return 0
    except Exception as e:
        print(f"❌ 브라우저 실행 실패: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
