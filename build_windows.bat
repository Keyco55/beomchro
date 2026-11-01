@echo off
REM ==============================================================================
REM BEOMCHRO Windows Standalone EXE One-Click Build
REM ==============================================================================

chcp 65001 > nul
cd /d "%~dp0"

echo [INFO] 가상환경 활성화 및 PyInstaller 빌드 시작...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

python build_windows_exe.py
pause
