#!/usr/bin/env python3
"""
BEOMCHRO Windows Standalone EXE Builder
Uses PyInstaller to bundle beomchro_core into a single executable.
"""

import sys
import subprocess
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent

def build():
    print("==================================================================")
    print("⚡ BEOMCHRO Windows EXE Builder (PyInstaller)")
    print("==================================================================")

    # Check/install pyinstaller
    try:
        import PyInstaller
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--name=BEOMCHRO",
        f"--add-data=simulator{';' if sys.platform == 'win32' else ':'}simulator",
        f"--add-data=extension{';' if sys.platform == 'win32' else ':'}extension",
        "--clean",
        "beomchro_core.py",
    ]

    print("🚀 Running PyInstaller...")
    subprocess.run(cmd, check=True)
    print("\n✔ 빌드 완료! dist/BEOMCHRO 폴더에서 실행 파일을 확인할 수 있습니다.")

if __name__ == "__main__":
    build()
