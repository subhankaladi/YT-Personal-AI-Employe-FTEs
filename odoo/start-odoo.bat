@echo off
REM Odoo Startup Script with Health Check
REM Waits for Odoo to be fully initialized

cd /d "%~dp0"

echo ============================================================
echo   Odoo ERP Startup - Gold Tier
echo ============================================================
echo.
echo Starting Odoo containers...
docker-compose up -d

echo.
echo Waiting for Odoo to initialize (this takes 2-3 minutes)...
echo.

REM Wait loop with status checks
for /l %%i in (1,1,10) do (
    echo Check %%i/10: Waiting 20 seconds...
    timeout /t 20 /nobreak >nul
    
    echo Checking Odoo status...
    curl -s http://localhost:8069 >nul 2>&1
    if not errorlevel 1 (
        echo.
        echo [OK] Odoo is responding!
        echo.
        goto :success
    ) else (
        echo [WAITING] Odoo not ready yet...
        echo.
    )
)

echo.
echo [WARNING] Odoo is taking longer than expected to start
echo [INFO] Check logs: docker-compose logs odoo
echo.

:success
echo ============================================================
echo   Odoo is Ready!
echo ============================================================
echo.
echo Access Odoo at: http://localhost:8069
echo.
echo First Time Setup:
echo   1. Open http://localhost:8069 in your browser
echo   2. Create your database:
echo      - Database name: odoo
echo      - Email: admin@example.com
echo      - Password: admin  (CHANGE THIS!)
echo   3. Install these modules:
echo      - Accounting
echo      - Invoicing
echo      - CRM
echo      - Contacts
echo.
echo After setup, update odoo_mcp_server.py with your credentials
echo.
echo ============================================================
