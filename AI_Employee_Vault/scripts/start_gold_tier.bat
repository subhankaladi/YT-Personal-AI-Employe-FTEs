@echo off
REM Gold Tier Start Script
REM Starts all Gold Tier components

cd /d "%~dp0"

echo ============================================
echo AI Employee - Gold Tier Startup
echo ============================================
echo.

REM Check if Docker is running
echo [1/6] Checking Docker...
docker ps >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running!
    echo Please start Docker Desktop first.
    echo.
    pause
    exit /b 1
)
echo OK: Docker is running
echo.

REM Check if Odoo is running
echo [2/6] Checking Odoo...
cd ..\odoo
docker-compose ps | findstr "Up" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Odoo is not running
    echo Starting Odoo...
    docker-compose up -d
    echo Waiting for Odoo to start (this may take 2-3 minutes)...
    timeout /t 30 /nobreak >nul
) else (
    echo OK: Odoo is running
)
cd ..\AI_Employee_Vault\scripts
echo.

REM Check credentials
echo [3/6] Checking credentials...
if not exist "..\..\credentials.json" (
    echo WARNING: credentials.json not found
    echo Gmail watcher may not work without it
) else (
    echo OK: credentials.json found
)
echo.

REM Check Facebook session
echo [4/6] Checking Facebook session...
if exist "%USERPROFILE%\.facebook_session" (
    echo OK: Facebook session found
) else (
    echo WARNING: Facebook session not found
    echo Run: python facebook_watcher.py ..\ --login
)
echo.

REM Start MCP servers
echo [5/6] Starting MCP servers...

REM Start Odoo MCP
start "Odoo MCP Server" python odoo_mcp_server.py
echo   - Odoo MCP Server started

REM Start Facebook MCP
start "Facebook MCP Server" python facebook_mcp_server.py
echo   - Facebook MCP Server started

echo.

REM Start orchestrator
echo [6/6] Starting Gold Orchestrator...
start "Gold Orchestrator" python ralph_wiggum_loop.py ..\ --orchestrator --interval 30
echo   - Gold Orchestrator started

echo.
echo ============================================
echo Gold Tier Components Started!
echo ============================================
echo.
echo Running Components:
echo   ✓ Odoo MCP Server
echo   ✓ Facebook MCP Server
echo   ✓ Gold Orchestrator (Ralph Wiggum Loop)
echo.
echo Additional watchers (run in separate terminals if needed):
echo   - Gmail Watcher:    python gmail_watcher.py ..\ --credentials ..\..\credentials.json
echo   - WhatsApp Watcher: python whatsapp_watcher.py ..\
echo   - Facebook Watcher: python facebook_watcher.py ..\ --interval 300
echo   - File Watcher:     python filesystem_watcher.py ..\
echo.
echo To stop all components:
echo   1. Close the terminal windows
echo   2. Or press Ctrl+C in each window
echo.
echo To view status:
echo   - Odoo: http://localhost:8069
echo   - Docker: docker-compose ps
echo   - Logs: cd ..\Logs ^&^& type *-main.jsonl
echo.
echo ============================================
echo.
pause
