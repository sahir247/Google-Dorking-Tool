@echo off
title Google Dorking Tool - Dependencies Installer
echo ========================================================
echo   Google Dorking Tool v1.2 - Dependencies Installer
echo ========================================================
echo.

where uv >nul 2>&1
if not errorlevel 1 (
    echo [INFO] Found 'uv' package manager. Installing with uv pip...
    uv pip install -r "%~dp0requirements.txt"
    if not errorlevel 1 goto success
)

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not found in PATH!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [INFO] Installing required Python packages using pip...
python -m pip install -r "%~dp0requirements.txt" --break-system-packages 2>nul || python -m pip install -r "%~dp0requirements.txt"

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

:success
echo.
echo ========================================================
echo   Dependencies successfully installed!
echo   You can now launch the application using run.bat
echo ========================================================
pause
