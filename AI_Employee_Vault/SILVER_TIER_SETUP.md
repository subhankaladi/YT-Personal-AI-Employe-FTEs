# Silver Tier Setup Guide

Complete setup instructions for AI Employee Silver Tier with Gmail Watcher and LinkedIn Watcher.

## Overview

Silver Tier includes:
- **Gmail Watcher** - Monitor Gmail for important emails
- **LinkedIn Watcher/Poster** - Monitor notifications and post updates
- **File System Watcher** - Monitor Inbox folder (from Bronze)
- **Orchestrator** - Coordinate all watchers
- **Approval Workflow** - Human-in-the-loop for sensitive actions

## Prerequisites

- Python 3.13+ installed
- Qwen Code installed
- Gmail API credentials (credentials.json)
- LinkedIn account

## Step 1: Install Dependencies

```bash
cd AI_Employee_Vault\scripts

# Install all Silver Tier dependencies
pip install -r requirements_silver.txt

# Install Playwright browsers
playwright install chromium
```

## Step 2: Set Up Gmail Watcher

### 2.1 Verify Credentials

Your `credentials.json` should be in the project root:
```
C:\Users\a\Documents\GitHub\YT-Personal-AI-Employe-FTEs\credentials.json
```

### 2.2 Authenticate Gmail

Run authentication (browser will open):

```bash
cd AI_Employee_Vault\scripts
python gmail_watcher.py ..\ --authenticate --credentials ..\..\credentials.json
```

**Steps:**
1. Browser opens automatically
2. Click the URL if it doesn't open
3. Sign in with your Google account
4. Grant permissions when prompted
5. Page shows "Authentication successful"
6. Token saved to `AI_Employee_Vault\.gmail_token.pkl`

### 2.3 Test Gmail Watcher

```bash
python gmail_watcher.py ..\ --credentials ..\..\credentials.json
```

Press `Ctrl+C` to stop after verifying it runs.

### 2.4 Configure Gmail Keywords

Edit keywords in command or create config:

```bash
python gmail_watcher.py ..\ -k urgent invoice payment asap deadline --credentials ..\..\credentials.json
```

## Step 3: Set Up LinkedIn Watcher

### 3.1 Authenticate LinkedIn

```bash
cd AI_Employee_Vault\scripts
python linkedin_watcher.py ..\ --authenticate
```

**Steps:**
1. Browser opens to LinkedIn login
2. Log in manually
3. Wait for feed to load
4. Close browser
5. Session saved to `AI_Employee_Vault\.linkedin_session\`

### 3.2 Test LinkedIn Posting

```bash
python linkedin_watcher.py ..\ --post "Testing AI Employee Silver Tier! #automation #AI"
```

### 3.3 Test LinkedIn Notifications Check

```bash
python linkedin_watcher.py ..\ --check
```

## Step 4: Configure Watchers

### Gmail Config (Optional)

Create `scripts/gmail_config.json`:

```json
{
  "credentials_path": "C:\\Users\\a\\Documents\\GitHub\\YT-Personal-AI-Employe-FTEs\\credentials.json",
  "token_path": "AI_Employee_Vault\\.gmail_token.pkl",
  "check_interval": 120,
  "keywords": ["urgent", "invoice", "payment", "asap"],
  "label_filter": "IMPORTANT"
}
```

### LinkedIn Config (Optional)

Create `scripts/linkedin_config.json`:

```json
{
  "session_path": "AI_Employee_Vault\\.linkedin_session",
  "check_interval": 300,
  "keywords": ["comment", "message", "connection"],
  "hashtags": ["business", "tech", "AI"],
  "require_approval": true
}
```

## Step 5: Run All Watchers

### Option A: Manual Start

Open 3 terminals:

**Terminal 1 - Gmail Watcher:**
```bash
cd AI_Employee_Vault\scripts
python gmail_watcher.py ..\ --credentials ..\..\credentials.json
```

**Terminal 2 - LinkedIn Watcher:**
```bash
cd AI_Employee_Vault\scripts
python linkedin_watcher.py ..\
```

**Terminal 3 - File Watcher + Orchestrator:**
```bash
cd AI_Employee_Vault\scripts
python orchestrator.py ..\ --interval 30
```

### Option B: Windows Batch File

Create `scripts/start_all.bat`:

```batch
@echo off
cd /d "%~dp0"

echo Starting AI Employee Silver Tier...
echo.

REM Start Gmail Watcher
start "Gmail Watcher" python gmail_watcher.py ..\ --credentials ..\..\credentials.json

REM Start LinkedIn Watcher
start "LinkedIn Watcher" python linkedin_watcher.py ..\

REM Start Orchestrator
start "Orchestrator" python orchestrator.py ..\ --interval 30

echo All watchers started!
echo Press any key to exit this window...
pause >nul
```

Run:
```bash
start_all.bat
```

## Step 6: Verify System Working

### Check Logs

Watchers should log:
```
2026-02-25 11:40:00 - GmailWatcher - INFO - Found 0 new emails
2026-02-25 11:40:00 - LinkedInWatcher - INFO - Found 0 new notifications
2026-02-25 11:40:00 - Orchestrator - INFO - Dashboard updated
```

### Test with Real Email

1. Send yourself an email with subject "Test Invoice"
2. Mark it as Important in Gmail
3. Wait up to 2 minutes
4. Check `AI_Employee_Vault\Needs_Action\` for new EMAIL_*.md file

### Test with LinkedIn Post

```bash
python linkedin_watcher.py ..\ --post "Silver Tier test post from AI Employee!" --hashtags AI automation
```

Check LinkedIn for your post.

## Step 7: Set Up Approval Workflow

For sensitive actions, approval is required:

1. Watcher creates file in `Pending_Approval/`
2. You review the file
3. Move to `Approved/` to execute
4. Move to `Rejected/` to cancel

### Test Approval Workflow

```bash
python approval_manager.py ..\ --list
python approval_manager.py ..\ --check
python approval_manager.py ..\ --process-approved
```

## Troubleshooting

### Gmail Watcher Issues

**"Token not found"**
```bash
python gmail_watcher.py ..\ --authenticate --credentials ..\..\credentials.json
```

**"No emails found"**
- Ensure emails are marked Important
- Check keywords match email content
- Verify Gmail API is enabled

### LinkedIn Watcher Issues

**"Session not found"**
```bash
python linkedin_watcher.py ..\ --authenticate
```

**"Post failed"**
- LinkedIn may have updated UI
- Try re-authenticating
- Check browser console for errors

### General Issues

**"Module not found"**
```bash
pip install -r requirements_silver.txt
playwright install chromium
```

**"Port already in use"**
- Close other Python processes
- Check Task Manager for stuck python.exe

## Daily Operations

### Morning Check

```bash
# Check pending approvals
python approval_manager.py ..\ --list

# View dashboard
type ..\Dashboard.md
```

### Process Approved Items

```bash
python approval_manager.py ..\ --process-approved
```

### Stop All Watchers

Close terminal windows or press `Ctrl+C` in each.

## Next Steps

1. Configure Windows Task Scheduler for auto-start
2. Set up daily briefing generation
3. Add more keywords for filtering
4. Customize approval thresholds in Company_Handbook.md

## Security Notes

- Never commit `credentials.json` or `*token.pkl` to git
- Keep session files private
- Review approval requests before approving
- Monitor logs regularly

---

*Silver Tier Setup Complete!*

For support, refer to:
- [Gmail Watcher Skill](../.qwen/skills/gmail-watcher/SKILL.md)
- [LinkedIn Watcher Skill](../.qwen/skills/linkedin-auto-poster/SKILL.md)
- [Approval Workflow Skill](../.qwen/skills/human-in-the-loop-approval/SKILL.md)
