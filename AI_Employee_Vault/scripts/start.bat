@echo off
REM Start AI Employee - Windows Batch Script
REM This script starts the File System Watcher and Orchestrator

echo ============================================
echo   AI Employee - Bronze Tier
echo ============================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Checking dependencies...
pip install -q watchdog 2>nul

REM Get vault path
set VAULT_PATH=%~dp0..

echo.
echo Starting File System Watcher...
echo Watching folder: %VAULT_PATH%\Inbox
echo.
echo Drop files into the Inbox folder to trigger processing.
echo Press Ctrl+C to stop.
echo.

REM Start the watcher
python scripts\filesystem_watcher.py "%VAULT_PATH%"

pause
