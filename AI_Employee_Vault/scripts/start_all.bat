@echo off
REM Start All AI Employee Silver Tier Watchers
REM This script starts Gmail Watcher, LinkedIn Watcher, and Orchestrator

echo ============================================
echo   AI Employee - Silver Tier
echo   Starting all watchers...
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

REM Check if credentials exist
if not exist "..\..\credentials.json" (
    echo ERROR: credentials.json not found in project root
    echo Please create Gmail API credentials first
    pause
    exit /b 1
)

echo Starting Gmail Watcher...
echo Monitoring Gmail for important emails...
start "Gmail Watcher" python gmail_watcher.py ..\ --credentials ..\..\credentials.json

timeout /t 2 /nobreak >nul

echo.
echo Starting LinkedIn Watcher...
echo Monitoring LinkedIn for notifications...
start "LinkedIn Watcher" python linkedin_watcher.py ..\

timeout /t 2 /nobreak >nul

echo.
echo Starting Orchestrator...
echo Coordinating all watchers...
start "Orchestrator" python orchestrator.py ..\ --interval 30

timeout /t 2 /nobreak >nul

echo.
echo ============================================
echo   All watchers started successfully!
echo ============================================
echo.
echo Watchers are running in separate windows.
echo.
echo To stop watchers:
echo   1. Close each watcher window, OR
echo   2. Press Ctrl+C in each window
echo.
echo Check AI_Employee_Vault\Needs_Action\ for new items.
echo.
pause
