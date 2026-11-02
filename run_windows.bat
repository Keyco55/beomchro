@echo off
setlocal EnableDelayedExpansion
title BEOMCHRO v2.1 - NOL Ticket 0ms Queue Interceptor
cd /d "%~dp0"

echo ==========================================================================
echo   [BEOMCHRO v2.1] Windows Native Engine Starting...
echo   Working Directory: %~dp0
echo ==========================================================================

if not exist "%~dp0beomchro_win_native.ps1" (
    echo.
    echo [ERROR] Required files not found in current folder!
    echo Did you double-click inside the .zip file without extracting it?
    echo Please right-click the .zip file and click [Extract All] first!
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('[ZIP Extract Required]`n`nPlease extract (Unzip) the downloaded .zip file to a normal folder first, then double-click run_windows.bat!', 'BEOMCHRO v2.1', 'OK', 'Warning')"
    pause
    exit /b 1
)

if not exist "%~dp0extension\manifest.json" (
    echo.
    echo [ERROR] extension\manifest.json not found! Please extract the full .zip file first.
    pause
    exit /b 1
)

chcp 65001 >nul 2>&1
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0beomchro_win_native.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [WARN] Standard launch returned code %ERRORLEVEL%. Retrying via memory stream...
    powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Invoke-Expression ([System.IO.File]::ReadAllText('%~dp0beomchro_win_native.ps1', [System.Text.Encoding]::UTF8))"
)

echo.
pause
