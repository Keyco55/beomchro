@echo off
REM ==============================================================================
REM BEOMCHRO (범크로) Windows Launcher
REM NOL-TICKET ULTRA FAST QUEUE INTERCEPTOR v2.0
REM ==============================================================================

chcp 65001 > nul
title BEOMCHRO v2.0 - Nol-Ticket Queue Interceptor
cd /d "%~dp0"

echo ==================================================================
echo ⚡ BEOMCHRO HYBRID QUEUE INTERCEPTOR v2.0 (Windows)
echo ==================================================================

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python이 설치되어 있지 않거나 PATH에 등록되지 않았습니다.
    echo https://www.python.org 에서 Python 3.9 이상을 설치해 주십시오.
    pause
    exit /b 1
)

if not exist ".venv" (
    echo [INFO] 가상환경(.venv) 생성 중...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

if exist "requirements.txt" (
    echo [INFO] 필수 패키지 점검 및 설치 중...
    python -m pip install --upgrade pip --quiet
    pip install -r requirements.txt --quiet
)

echo [INFO] BEOMCHRO TUI 대시보드 실행...
python beomchro_core.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo 실행 중 오류가 발생했습니다.
    pause
)
