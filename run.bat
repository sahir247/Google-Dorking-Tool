@echo off
title Google Dorking Tool v1.2
cd /d "%~dp0"

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0GoogleDorkingTool-v1.2.py"
    goto end
)

where uv >nul 2>&1
if not errorlevel 1 (
    uv run --with PySide6 --with requests --with cryptography python "%~dp0GoogleDorkingTool-v1.2.py"
    goto end
)

python "%~dp0GoogleDorkingTool-v1.2.py"
if errorlevel 1 (
    echo.
    echo [INFO] Dependencies might be missing. Running install_requirements.bat...
    call "%~dp0install_requirements.bat"
    python "%~dp0GoogleDorkingTool-v1.2.py"
)

:end
