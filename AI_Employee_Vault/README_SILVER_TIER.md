# AI Employee - Silver Tier

A functional autonomous AI assistant that manages personal and business affairs using **Qwen Code** as the reasoning engine and **Obsidian** as the dashboard/memory.

This is the **Silver Tier** implementation containing all Bronze features plus:
- ✅ **Multiple Watcher scripts** (Gmail, WhatsApp, File System)
- ✅ **LinkedIn Auto-Poster** for business promotion
- ✅ **Plan Generator** for multi-step task breakdown
- ✅ **Email MCP Server** for sending emails
- ✅ **Human-in-the-Loop Approval Workflow**
- ✅ **Windows Task Scheduler** integration

## Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Dashboard |
| [Playwright](https://playwright.dev) | Latest | Browser automation |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers |

### Installation

1. **Install Python dependencies:**

```bash
cd AI_Employee_Vault/scripts
pip install -r requirements_silver.txt
```

2. **Install Playwright browsers:**

```bash
playwright install chromium
```

3. **Verify Qwen Code:**

```bash
qwen --version
```

4. **Open vault in Obsidian:**

```
File → Open Folder → Select AI_Employee_Vault
```

## Silver Tier Features

### 1. Multiple Watchers

#### Gmail Watcher
Monitors Gmail for important/unread emails.

```bash
# First time: authenticate
python gmail_watcher.py ..\ --authenticate

# Run watcher
python gmail_watcher.py ..\ --interval 120
```

**Config:** `scripts/gmail_config.json`

#### WhatsApp Watcher
Monitors WhatsApp Web for messages with keywords.

```bash
python whatsapp_watcher.py ..\ --interval 30
```

**Keywords:** urgent, asap, invoice, payment, help, pricing

#### File System Watcher
Monitors Inbox folder for dropped files.

```bash
python filesystem_watcher.py ..\
```

### 2. LinkedIn Auto-Poster

Automatically post updates to LinkedIn for business promotion.

```bash
# Create draft for approval
python linkedin_poster.py ..\ --draft --topic "AI trends" --tone professional

# Post immediately (use with caution)
python linkedin_poster.py ..\ --post "Your post content" --hashtags business tech

# Process approved posts
python linkedin_poster.py ..\ --process-approved
```

**Config:** `scripts/linkedin_config.json`

⚠️ **Warning:** LinkedIn automation may violate ToS. Use at your own risk.

### 3. Email MCP Server

Send emails via Gmail API.

```bash
# First time: authenticate
python email_mcp_server.py --authenticate

# Run server
python email_mcp_server.py --port 8809
```

**Tools:**
- `email_send` - Send email immediately
- `email_draft` - Create draft
- `email_search` - Search emails
- `email_reply` - Reply to email

### 4. Plan Generator

Qwen Code creates structured plans for multi-step tasks.

```bash
cd AI_Employee_Vault
qwen "Create a plan for processing the email in Needs_Action"
```

**Output:** `/Plans/PLAN_[task]_[timestamp].md`

### 5. Human-in-the-Loop Approval

Require approval for sensitive actions.

```bash
# Check for expired approvals
python approval_manager.py ..\ --check

# Process approved items
python approval_manager.py ..\ --process-approved

# List pending approvals
python approval_manager.py ..\ --list
```

**Workflow:**
1. AI creates approval request in `/Pending_Approval`
2. Human reviews and moves to `/Approved` or `/Rejected`
3. Orchestrator executes approved actions

### 6. Windows Task Scheduler

Automate tasks with Windows Task Scheduler.

```powershell
# Create scheduled tasks
python scripts\setup_tasks.ps1

# View tasks
Get-ScheduledTask -TaskPath "\AI Employee\"
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SILVER TIER ARCHITECTURE                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │  Gmail   │  │ WhatsApp │  │   File   │                 │
│  │ Watcher  │  │ Watcher  │  │  Watcher │                 │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                 │
│       │             │             │                        │
│       └─────────────┼─────────────┘                        │
│                     ▼                                      │
│           ┌─────────────────┐                              │
│           │  Needs_Action/  │                              │
│           └────────┬────────┘                              │
│                    │                                       │
│                    ▼                                       │
│  ┌──────────────────────────────────────────────────────┐ │
│  │              QWEN CODE (Brain)                       │ │
│  │  - Reads action files                                │ │
│  │  - Creates plans for complex tasks                   │ │
│  │  - Requests approval for sensitive actions           │ │
│  └──────────────────────────────────────────────────────┘ │
│                    │                                       │
│        ┌───────────┼───────────┐                          │
│        ▼           ▼           ▼                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                  │
│  │ Pending  │ │ Approved │ │   Done   │                  │
│  │ Approval │ │          │ │          │                  │
│  └────┬─────┘ └────┬─────┘ └──────────┘                  │
│       │            │                                      │
│       │            ▼                                      │
│       │     ┌──────────────┐                              │
│       │     │  Orchestrator│                              │
│       │     │  + MCP Server│                              │
│       │     └──────────────┘                              │
│       │            │                                      │
│       ▼            ▼                                      │
│  ┌─────────────────────────┐                              │
│  │   External Actions      │                              │
│  │  - Send Email           │                              │
│  │  - Post to LinkedIn     │                              │
│  │  - Browser Automation   │                              │
│  └─────────────────────────┘                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status
├── Company_Handbook.md       # Rules & approval thresholds
├── Business_Goals.md         # Goals & metrics
├── README.md                 # This file
├── Inbox/                    # Drop files here
├── Needs_Action/             # Items to process
│   ├── EMAIL_*.md           # Gmail emails
│   ├── WHATSAPP_*.md        # WhatsApp messages
│   └── FILE_*.md            # Dropped files
├── Plans/                    # Multi-step task plans
├── Pending_Approval/         # Awaiting human decision
├── Approved/                 # Approved, ready to execute
├── Rejected/                 # Rejected actions
├── Done/                     # Completed items
├── Accounting/               # Transactions
├── Briefings/                # Daily/weekly briefings
├── Logs/                     # Action logs
├── Invoices/                 # Invoice templates
└── scripts/
    ├── base_watcher.py       # Base watcher class
    ├── filesystem_watcher.py # File system monitor
    ├── gmail_watcher.py      # Gmail monitor
    ├── whatsapp_watcher.py   # WhatsApp monitor
    ├── orchestrator.py       # Main orchestration
    ├── approval_manager.py   # Approval workflow
    ├── email_mcp_server.py   # Email sending
    ├── linkedin_poster.py    # LinkedIn posting
    ├── requirements_silver.txt
    └── start.bat             # Windows starter
```

## Approval Thresholds

Configure in `Company_Handbook.md`:

| Action Type | Auto-Approve | Requires Approval |
|-------------|--------------|-------------------|
| Email to known contact | Yes | No |
| Email to new contact | No | Yes |
| Email with attachment | No | Yes |
| Payment < $50 | Yes | No |
| Payment ≥ $50 | No | Yes |
| LinkedIn post | No | Yes (always) |
| File delete | No | Yes (always) |

## Usage Examples

### Example 1: Process Email Invoice Request

1. **Gmail Watcher** detects new email about invoice
2. Creates `EMAIL_*.md` in `Needs_Action/`
3. **Orchestrator** triggers Qwen Code
4. **Qwen** reads email, creates plan in `Plans/`
5. Plan identifies email send requires approval
6. Creates `APPROVAL_email_send_*.md` in `Pending_Approval`
7. **You** review and move to `Approved`
8. **Email MCP** sends email
9. Action moved to `Done`

### Example 2: LinkedIn Post for Sales

1. Drop file `linkedin_topic.txt` in `Inbox`
2. **File Watcher** creates action file
3. **Qwen** generates post content from topic
4. Creates approval file in `Pending_Approval`
5. **You** approve by moving to `Approved`
6. **LinkedIn Poster** posts update
7. Screenshot saved to `Done`

### Example 3: Multi-Step Project

```bash
cd AI_Employee_Vault

# Qwen creates comprehensive plan
qwen "Create a plan for processing all pending items and generating weekly report"

# Review plan
cat Plans/PLAN_weekly_report_*.md

# Execute plan step by step
qwen "Execute the next pending step in the weekly report plan"
```

## Scheduled Tasks (Windows)

### Daily Briefing - 8:00 AM

```powershell
# Creates daily briefing from previous day's activity
Get-ScheduledTask -TaskName "AI Employee - Daily Briefing"
```

### Continuous Watchers - At Log On

```powershell
# Runs watchers in background
Get-ScheduledTask -TaskName "AI Employee - Watchers"
```

### Approval Processing - Every Hour

```powershell
# Checks and processes approved items
Get-ScheduledTask -TaskName "AI Employee - Process Approvals"
```

## Configuration

### Gmail Config (`scripts/gmail_config.json`)

```json
{
  "credentials_path": "C:\\Users\\You\\gmail_credentials.json",
  "token_path": "C:\\Users\\You\\gmail_token.pkl",
  "check_interval": 120,
  "keywords": ["urgent", "invoice", "payment"],
  "label_filter": "IMPORTANT"
}
```

### WhatsApp Config (`scripts/whatsapp_config.json`)

```json
{
  "session_path": "C:\\Users\\You\\whatsapp_session",
  "check_interval": 30,
  "keywords": ["urgent", "asap", "invoice", "payment"],
  "quiet_hours": {"start": 22, "end": 6}
}
```

### LinkedIn Config (`scripts/linkedin_config.json`)

```json
{
  "session_path": "C:\\Users\\You\\linkedin_session",
  "post_schedule": {
    "enabled": true,
    "time": "09:00",
    "days": ["monday", "wednesday", "friday"]
  },
  "hashtags": ["business", "consulting", "tech"],
  "require_approval": true
}
```

## Troubleshooting

### Gmail Watcher Issues

| Issue | Solution |
|-------|----------|
| "Token not found" | Run with `--authenticate` |
| No emails detected | Check Gmail API enabled |
| "Invalid credentials" | Re-authenticate |

### WhatsApp Watcher Issues

| Issue | Solution |
|-------|----------|
| QR code every time | Session not saving |
| No messages found | Ensure messages are unread |
| Browser crashes | Update Playwright |

### LinkedIn Poster Issues

| Issue | Solution |
|-------|----------|
| Login fails | LinkedIn may block automation |
| Post button not found | UI changed, update selectors |
| Account restricted | Stop automation |

### Approval Workflow Issues

| Issue | Solution |
|-------|----------|
| Not processing | Check orchestrator running |
| Files stuck | Verify Qwen Code works |
| Too many approvals | Adjust thresholds |

## Security Notes

⚠️ **Important:**

1. **Never commit** credentials or tokens to git
2. **Store secrets** in environment variables or secure location
3. **Use app-specific passwords** if 2FA enabled
4. **Rotate credentials** regularly
5. **Review audit logs** in `/Logs`
6. **WhatsApp/LinkedIn automation** may violate ToS - use at own risk

## Monitoring

### Check System Status

```bash
# View dashboard
cat Dashboard.md

# Check pending approvals
python approval_manager.py ..\ --list

# View recent logs
cat Logs\*-approvals.jsonl
```

### Health Check Script

Create `health_check.ps1`:

```powershell
Write-Host "AI Employee Health Check"
Write-Host "========================"
Write-Host ""

$watchers = @("filesystem_watcher", "gmail_watcher", "whatsapp_watcher")
foreach ($w in $watchers) {
    $process = Get-Process -Name "python" -ErrorAction SilentlyContinue | 
               Where-Object {$_.CommandLine -like "*$w*"}
    if ($process) {
        Write-Host "✓ $w running" -ForegroundColor Green
    } else {
        Write-Host "✗ $w NOT running" -ForegroundColor Red
    }
}

$pending = (Get-ChildItem "Pending_Approval\*.md" -ErrorAction SilentlyContinue).Count
Write-Host ""
Write-Host "Pending approvals: $pending"
```

## Next Steps (Gold Tier)

To upgrade to Gold Tier, add:
- [ ] Odoo accounting integration via MCP
- [ ] Facebook/Instagram posting
- [ ] Twitter (X) integration
- [ ] Weekly CEO Briefing generation
- [ ] Error recovery & graceful degradation
- [ ] Ralph Wiggum loop for persistence
- [ ] Comprehensive audit logging

## Resources

- [Hackathon Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Gmail Watcher Skill](../.qwen/skills/gmail-watcher/SKILL.md)
- [WhatsApp Watcher Skill](../.qwen/skills/whatsapp-watcher/SKILL.md)
- [LinkedIn Auto-Poster Skill](../.qwen/skills/linkedin-auto-poster/SKILL.md)
- [Approval Workflow Skill](../.qwen/skills/human-in-the-loop-approval/SKILL.md)
- [Plan Generator Skill](../.qwen/skills/plan-generator/SKILL.md)

---

*AI Employee v0.2 (Silver Tier) - Built for Personal AI Employee Hackathon 0*
