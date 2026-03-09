# Gold Tier Setup Guide

Complete setup instructions for AI Employee Gold Tier with Odoo, Facebook, and Ralph Wiggum Loop.

## Overview

Gold Tier includes all Silver Tier features plus:
- **Odoo 19.0 ERP** - Self-hosted accounting via Docker
- **Facebook Integration** - Post and monitor Facebook
- **Ralph Wiggum Loop** - Persistent multi-step task completion
- **CEO Briefing Generator** - Weekly autonomous business audits
- **Enhanced Logging** - Comprehensive audit trails

## Prerequisites

- All Silver Tier prerequisites
- Docker Desktop installed and running
- Facebook account (for testing)
- 20GB free disk space (for Odoo)

## Step 1: Install Gold Tier Dependencies

```bash
cd AI_Employee_Vault\scripts

# Install Gold Tier dependencies
pip install -r requirements_gold.txt

# Verify Playwright browsers
playwright install chromium
```

## Step 2: Set Up Odoo 19.0 (Docker)

### 2.1 Verify Docker

```bash
docker --version
docker-compose --version
```

### 2.2 Start Odoo

```bash
cd ..\..\odoo
docker-compose up -d

# Monitor startup (takes 2-3 minutes)
docker-compose logs -f
```

### 2.3 Access Odoo Web Interface

1. Open browser: http://localhost:8069
2. Create database:
   - Database name: `odoo`
   - Email: `admin@example.com`
   - Password: `admin` (CHANGE THIS!)
3. Install modules:
   - Accounting
   - Invoicing
   - CRM
   - Contacts

### 2.4 Configure Odoo MCP

Edit `odoo\odoo_mcp_server.py`:

```python
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_USERNAME = "admin@example.com"
ODOO_PASSWORD = "admin"  # Change after first login!
```

### 2.5 Test Odoo Connection

```bash
cd ..\AI_Employee_Vault\scripts

# Test Odoo MCP (will be integrated with Qwen Code)
python -c "
import sys
sys.path.append('../odoo')
from odoo_mcp_server import odoo_client

success = odoo_client.authenticate()
print(f'Odoo authentication: {\"Success\" if success else \"Failed\"}')
"
```

## Step 3: Set Up Facebook Graph API Integration

### 3.1 Create Facebook App

1. Visit: https://developers.facebook.com/apps/
2. Click **My Apps** → **Create App**
3. Select **Business** as app type
4. Fill in app details and create

### 3.2 Get Access Token

1. Visit: https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Click **Get Token** → **Get User Access Token**
4. Select permissions:
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_engagement`
   - ✅ `pages_read_user_content`
   - ✅ `pages_messaging`
   - ✅ `user_notifications`
5. Click **Generate Token** and approve
6. Copy the **Access Token**

### 3.3 Get Page ID (for business features)

1. In Graph API Explorer, run: `/me/accounts`
2. Find your page and copy the `id`
3. Copy the page's `access_token`

### 3.4 Configure Environment

Create `facebook\.env` file:

```bash
# facebook\.env
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
```

### 3.5 Test Facebook Integration

```bash
cd AI_Employee_Vault\scripts

# Verify token
python facebook_graph_watcher.py ..\ --verify

# Test monitoring
python facebook_graph_watcher.py ..\ --test
```

Expected output:
```
✓ Facebook access token is valid
Testing Facebook Graph API Watcher...
Found X recent notifications
```

⚠️ **Note:** See `facebook\FACEBOOK_SETUP.md` for detailed instructions.

## Step 4: Configure Ralph Wiggum Loop

### 4.1 Review Configuration

Edit `ralph_wiggum_loop.py` if needed:

```python
max_iterations = 10  # Adjust based on task complexity
approval_timeout = 24  # Hours to wait for approval
check_interval = 30  # Seconds between checks
```

### 4.2 Test Ralph Loop

```bash
# Create a test task
echo "Test task" > ..\Needs_Action\TEST_TASK.md

# Run Ralph loop on test task
python ralph_wiggum_loop.py ..\ ^
  --prompt "Process TEST_TASK.md and move to Done when complete" ^
  --task-id test_001 ^
  --max-iterations 3 ^
  -v
```

## Step 5: Configure CEO Briefing Generator

### 5.1 Update Business Goals

Edit `..\Business_Goals.md`:

```markdown
## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $4,500

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Invoice payment rate | > 90% | < 80% |
| Software costs | < $500/month | > $600/month |
```

### 5.2 Test Briefing Generation

```bash
# Generate current week's briefing
python ceo_briefing_generator.py ..\

# View generated briefing
cat ..\Briefings\*_Monday_Briefing.md
```

### 5.3 Schedule Weekly Briefing

```powershell
# Create Windows Task Scheduler entry
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "ceo_briefing_generator.py ..\" `
  -WorkingDirectory "C:\Users\a\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts"

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7am

Register-ScheduledTask -TaskName "AI Employee - Weekly CEO Briefing" `
  -Action $action -Trigger $trigger -RunLevel Highest
```

## Step 6: Run All Gold Tier Components

### Option A: Manual Start (Development)

Open 4 terminals:

**Terminal 1 - Odoo MCP:**
```bash
cd odoo
python odoo_mcp_server.py
```

**Terminal 2 - Facebook MCP:**
```bash
cd AI_Employee_Vault\scripts
python facebook_mcp_server.py
```

**Terminal 3 - Watchers:**
```bash
cd AI_Employee_Vault\scripts

# Start all watchers
python gmail_watcher.py ..\ --credentials ..\..\credentials.json
# In another terminal:
python whatsapp_watcher.py ..\
# In another terminal:
python facebook_watcher.py ..\ --interval 300
```

**Terminal 4 - Orchestrator:**
```bash
cd AI_Employee_Vault\scripts
python ralph_wiggum_loop.py ..\ --orchestrator --interval 30 -v
```

### Option B: Gold Tier Batch File

Create `scripts\start_gold_tier.bat`:

```batch
@echo off
cd /d "%~dp0"

echo Starting AI Employee Gold Tier...
echo.

REM Check Docker
docker-compose ps >nul 2>&1
if errorlevel 1 (
    echo WARNING: Docker not running. Start Odoo manually:
    echo cd ..\odoo ^&^& docker-compose up -d
)

REM Start Odoo MCP
start "Odoo MCP" python odoo_mcp_server.py

REM Start Facebook MCP
start "Facebook MCP" facebook_mcp_server.py

REM Start Orchestrator with Ralph Loop
start "Gold Orchestrator" python ralph_wiggum_loop.py ..\ --orchestrator --interval 30

echo Gold Tier started!
echo.
echo Components:
echo - Odoo MCP Server
echo - Facebook MCP Server
echo - Ralph Wiggum Orchestrator
echo.
echo Run watchers separately or use start_all.bat
pause
```

### Option C: Windows Task Scheduler (Production)

```powershell
# Import Gold Tier tasks
python scripts\setup_gold_tasks.ps1

# View scheduled tasks
Get-ScheduledTask -TaskPath "\AI Employee\Gold Tier\"
```

## Step 7: Verify Gold Tier Setup

### 7.1 Check All Components

```bash
# Run health check
python health_check_gold.ps1

# Or manually verify:
# 1. Odoo: http://localhost:8069
# 2. Docker: docker-compose ps
# 3. Pending approvals: ls ..\Pending_Approval
# 4. Ralph state: ls ..\Plans\STATE_*.json
# 5. Logs: ls ..\Logs\
```

### 7.2 Test End-to-End Flow

1. **Create test invoice request:**
   ```bash
   echo "Please create invoice for Client X, $500 for consulting" > ..\Inbox\test_invoice.txt
   ```

2. **Wait for File Watcher** (or trigger manually):
   ```bash
   python filesystem_watcher.py ..\
   ```

3. **Check Needs_Action:**
   ```bash
   ls ..\Needs_Action\FILE_*.md
   ```

4. **Orchestrator should process** (wait 30 seconds)

5. **Check for approval file:**
   ```bash
   ls ..\Pending_Approval\
   ```

6. **Approve (move to Approved):**
   ```bash
   mv ..\Pending_Approval\*.md ..\Approved\
   ```

7. **Check Done folder:**
   ```bash
   ls ..\Done\
   ```

8. **Verify Odoo invoice:**
   - Open http://localhost:8069
   - Go to Accounting → Invoices
   - Should see new invoice

## Troubleshooting

### Odoo Not Starting

```bash
# Check Docker
docker ps -a | findstr odoo

# View logs
docker-compose logs odoo

# Restart
docker-compose down
docker-compose up -d

# Rebuild if needed
docker-compose build --no-cache
```

### Facebook Login Fails

```bash
# Clear session
rm -r %USERPROFILE%\.facebook_session

# Re-authenticate
python facebook_watcher.py ..\ --login
```

### Ralph Loop Stuck

```bash
# Check state files
cat Plans\STATE_*.json

# View logs
cat Logs\ralph_*.log

# Kill stuck process
Get-Process python | Where-Object {$_.CommandLine -like "*ralph*"} | Stop-Process
```

### CEO Briefing Empty

```bash
# Check Business_Goals.md exists
cat ..\Business_Goals.md

# Check Done folder has files
ls ..\Done\*.md

# Run with verbose
python ceo_briefing_generator.py ..\ -v
```

## Daily Operations

### Morning Check (5 minutes)

```bash
# 1. View dashboard
cat ..\Dashboard.md

# 2. Check pending approvals
python approval_manager.py ..\ --list

# 3. Check Odoo status
docker-compose ps

# 4. View overnight logs
cat Logs\*-main.jsonl | Select-Object -Last 20
```

### Weekly Review (30 minutes)

```bash
# 1. Review CEO briefing
cat ..\Briefings\*_Monday_Briefing.md

# 2. Check Ralph loop performance
cat Plans\STATE_*.json | ConvertFrom-Json | Format-Table task_id, status, iteration

# 3. Audit Odoo invoices
# Open http://localhost:8069 → Accounting → Invoices

# 4. Review Facebook activity
python facebook_watcher.py ..\ --test
```

## Security Checklist

- [ ] Changed Odoo admin password from default
- [ ] Facebook credentials not stored in code
- [ ] Docker not exposed to public internet
- [ ] Audit logging enabled
- [ ] Credentials in environment variables
- [ ] Regular credential rotation scheduled

## Performance Tuning

### Odoo Optimization

Edit `odoo/docker-compose.yml`:

```yaml
services:
  odoo:
    command: --workers=4 --max-cron-threads=2
    # Increase for better performance
```

### Ralph Loop Optimization

Adjust in `ralph_wiggum_loop.py`:

```python
max_iterations = 5  # Reduce for simpler tasks
check_interval = 60  # Increase for lower resource usage
```

## Next Steps

1. **Customize approval thresholds** in Company_Handbook.md
2. **Set up email notifications** for pending approvals
3. **Configure business metrics** in Business_Goals.md
4. **Test end-to-end flows** with real scenarios
5. **Schedule regular reviews** of AI performance

## Resources

- [Gold Tier README](README_GOLD_TIER.md)
- [Odoo Documentation](https://www.odoo.com/documentation/19.0)
- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [Facebook Watcher](../.qwen/skills/facebook-watcher/SKILL.md)
- [Odoo MCP](../.qwen/skills/odoo-mcp/SKILL.md)

---

*Gold Tier Setup Complete!*

For support, refer to README_GOLD_TIER.md or the main hackathon document.
