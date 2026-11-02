@echo off
REM ==============================================================================
REM BEOMCHRO (범크로) v2.1 Windows One-Click Launcher (Zero-Python Supported!)
REM NOL-TICKET ULTRA FAST QUEUE INTERCEPTOR
REM ==============================================================================

chcp 65001 > nul
title BEOMCHRO v2.1 - NOL Ticket 0ms Queue Interceptor
cd /d "%~dp0"

REM 파이썬이 설치되어 있지 않아도 Windows 내장 엔진(beomchro_win_native.ps1)으로 100% 즉시 작동합니다!
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0beomchro_win_native.ps1"
    exit /b 0
)

if not exist ".venv" (
    echo [INFO] 최초 1회 실행 환경을 구성 중입니다...
    python -m venv .venv >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0beomchro_win_native.ps1"
        exit /b 0
    )
)

call .venv\Scripts\activate.bat >nul 2>&1
if exist "requirements.txt" (
    pip install -r requirements.txt --quiet >nul 2>&1
)

python beomchro_core.py %*
if %ERRORLEVEL% NEQ 0 (
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0beomchro_win_native.ps1"
)
