@echo off
cd /d "%~dp0"
echo [INFO] Building BEOMCHRO Standalone Windows EXE...
if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat
python build_windows_exe.py
pause
