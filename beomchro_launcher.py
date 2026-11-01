#!/usr/bin/env python3
"""
BEOMCHRO Browser Launcher v2.0
Detects installed browsers and launches a dedicated session with the 0ms extension pre-loaded.
"""

import sys
import os
import platform
import subprocess
from pathlib import Path

CURRENT_OS = platform.system()
IS_MACOS = CURRENT_OS == 'Darwin'
IS_WINDOWS = CURRENT_OS == 'Windows'
IS_LINUX = CURRENT_OS == 'Linux'

PROJECT_DIR = Path(__file__).resolve().parent
EXTENSION_DIR = PROJECT_DIR / "extension"
USER_DATA_DIR = Path.home() / ".beomchro" / "browser_profile"


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
        # Linux
        candidates = [
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/google-chrome-stable"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
        ]

    for p in candidates:
        if p.exists() and os.access(str(p), os.X_OK if not IS_WINDOWS else os.F_OK):
            return p

    # Fallback to PATH search
    for name in ["google-chrome", "chrome", "msedge", "whale", "chromium"]:
        found = subprocess.run(["which" if not IS_WINDOWS else "where", name], capture_output=True, text=True)
        if found.returncode == 0 and found.stdout.strip():
            first_line = found.stdout.strip().splitlines()[0]
            if Path(first_line).exists():
                return Path(first_line)

    return None


def launch_browser(target_urls=None, extension_path=None, profile_dir=None, dry_run=False):
    """Launch dedicated browser instance with auto-loaded extension."""
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
            # Fallback to local project profile if home directory is restricted
            data_dir = PROJECT_DIR / ".browser_profile"
            data_dir.mkdir(parents=True, exist_ok=True)

    if not target_urls:
        target_urls = ["http://localhost:8989"]

    args = [
        str(browser_exe),
        f"--load-extension={ext_dir.resolve()}",
        f"--user-data-dir={data_dir.resolve()}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-features=Translate,OptimizationHints",
        "--enable-features=NetworkService,NetworkServiceInProcess",
    ] + list(target_urls)

    if dry_run:
        print("[DRY-RUN] Browser Executable:", browser_exe)
        print("[DRY-RUN] Extension Path:", ext_dir)
        print("[DRY-RUN] Profile Dir:", data_dir)
        print("[DRY-RUN] Command:", " ".join(f'"{a}"' if " " in a else a for a in args))
        return None

    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc


def main():
    import argparse
    parser = argparse.ArgumentParser(description="BEOMCHRO Browser Launcher")
    parser.add_argument("--dry-run", action="store_true", help="Print command without launching")
    parser.add_argument("--url", nargs="*", default=["http://localhost:8989"], help="URLs to open")
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
