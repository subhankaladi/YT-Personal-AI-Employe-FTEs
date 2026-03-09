# AI Employee - Gold Tier

A fully autonomous AI assistant that manages personal and business affairs 24/7 using **Qwen Code** as the reasoning engine and **Obsidian** as the dashboard/memory.

This is the **Gold Tier** implementation containing all Silver features plus:
- ✅ **Odoo 19.0 Integration** - Full accounting ERP via Docker Compose
- ✅ **Facebook/Instagram Integration** - Post and monitor social media
- ✅ **Ralph Wiggum Loop** - Persistent multi-step task completion
- ✅ **Weekly CEO Briefing** - Autonomous business audit and reporting
- ✅ **Error Recovery** - Graceful degradation and retry logic
- ✅ **Comprehensive Audit Logging** - Full action tracking

## Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Dashboard |
| [Docker Desktop](https://docker.com) | Latest | Odoo ERP |
| [Playwright](https://playwright.dev) | Latest | Browser automation |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers |

### Installation

#### 1. Install Gold Tier Dependencies

```bash
cd AI_Employee_Vault\scripts
pip install -r requirements_gold.txt
playwright install chromium
```

#### 2. Start Odoo ERP (Docker)

```bash
# From project root
cd odoo
docker-compose up -d

# Wait 2-3 minutes for initialization
# Access Odoo: http://localhost:8069
# Default login: admin@example.com / admin
```

#### 3. Authenticate Facebook

```bash
cd AI_Employee_Vault\scripts
python facebook_watcher.py ..\ --login
```

#### 4. Start Gold Tier Orchestrator

```bash
# Run orchestrator with Ralph Wiggum loop
python ralph_wiggum_loop.py ..\ --orchestrator --interval 30

# Or run individual watchers
python start_all.bat
```

## Gold Tier Features

### 1. Odoo 19.0 Accounting Integration

Full ERP integration for invoicing, payments, and financial reporting.

#### Start Odoo

```bash
cd odoo
docker-compose up -d
docker-compose logs -f  # Monitor startup
```

#### Odoo MCP Server

```bash
# Start Odoo MCP server
python odoo_mcp_server.py

# Available tools:
# - odoo_create_invoice
# - odoo_search_invoices
# - odoo_create_partner
# - odoo_create_payment
# - odoo_get_account_summary
# - odoo_create_journal_entry
```

#### Example: Create Invoice via Odoo

```bash
# Using Qwen Code
qwen "Create an invoice for Client A, $1500 for consulting services"

# Or use MCP directly
python -c "
from odoo_mcp_server import odoo_client
odoo_client.authenticate()
result = odoo_client.execute_kw('account.move', 'create', [{
    'move_type': 'out_invoice',
    'partner_id': 1,
    'invoice_line_ids': [(0, 0, {
        'name': 'Consulting Services',
        'price_unit': 1500,
        'quantity': 1
    })]
}])
print(f'Invoice created: {result}')
"
```

### 2. Facebook Graph API Integration

Post to Facebook and monitor notifications/messages using the **official Facebook Graph API**.

**Benefits over browser automation:**
- ✅ ToS compliant (official API)
- ✅ More reliable (no UI selector breaks)
- ✅ No account restriction risk
- ✅ More features (insights, messages, analytics)

#### Facebook Setup

```bash
# 1. Create Facebook App at https://developers.facebook.com/apps/
# 2. Get Access Token from Graph API Explorer
# 3. Configure environment variables

# See facebook/FACEBOOK_SETUP.md for detailed setup
```

#### Facebook Graph API Watcher

```bash
# Verify token
python facebook_graph_watcher.py ..\ --verify

# Test Facebook monitoring
python facebook_graph_watcher.py ..\ --test

# Run continuous monitoring (checks every 5 minutes)
python facebook_graph_watcher.py ..\ --interval 300
```

#### Facebook Graph API MCP Server

```bash
# Start Facebook MCP server
cd facebook
python facebook_graph_mcp_server.py

# Available tools:
# - facebook_verify_token
# - facebook_create_post
# - facebook_create_photo_post
# - facebook_get_notifications
# - facebook_get_page_insights
# - facebook_get_posts
# - facebook_get_comments
# - facebook_get_messages
# - facebook_generate_hashtags
```

#### Example: Post to Facebook

```bash
# Using Qwen Code
qwen "Post to Facebook: Excited to announce our new AI consulting service! #AI #Business"

# Post with link
qwen "Post to Facebook about our new service with link to https://example.com"

# Get notifications
qwen "Check my Facebook notifications for urgent messages"

# Get page insights
qwen "Get my Facebook page insights for reach and engagement"
```

### 3. Ralph Wiggum Loop

Persistent multi-step task completion with automatic iteration.

```bash
# Run single task with Ralph loop
python ralph_wiggum_loop.py ..\ --prompt "Process all pending invoices and generate weekly report" --max-iterations 10

# Run as continuous orchestrator
python ralph_wiggum_loop.py ..\ --orchestrator --interval 30

# With verbose logging
python ralph_wiggum_loop.py ..\ --orchestrator -v
```

#### How It Works

1. **Task Detection**: Watchers create files in `/Needs_Action`
2. **Task Claiming**: Orchestrator moves to `/In_Progress/gold_tier`
3. **Claude Iteration**: Ralph loop keeps Claude working
4. **Approval Wait**: Pauses for human approval when needed
5. **Task Completion**: Moves to `/Done` when complete

### 4. Weekly CEO Briefing

Autonomous business audit and executive reporting.

```bash
# Generate current week's briefing
python ceo_briefing_generator.py ..\

# Generate for specific week
python ceo_briefing_generator.py ..\ --week-start 2026-03-01 --week-end 2026-03-07

# With Odoo integration
python ceo_briefing_generator.py ..\ --odoo-url http://localhost:8069
```

#### Briefing Contents

- **Executive Summary**: Overall business status
- **Revenue & Financials**: MTD revenue, expenses, profit
- **Completed Tasks**: This week's accomplishments
- **Bottlenecks**: Blocked tasks and delays
- **Proactive Suggestions**: AI-generated recommendations
- **Upcoming Deadlines**: Calendar integration
- **CEO Action Items**: Requires your attention

### 5. Error Recovery & Retry Logic

Graceful degradation when components fail.

```python
# Automatic retry with exponential backoff
@with_retry(max_attempts=3, base_delay=1, max_delay=60)
def send_email(to, subject, body):
    # Implementation with retry logic
    pass

# Watchdog process monitoring
python watchdog.py ..\  # Auto-restart failed processes
```

### 6. Comprehensive Audit Logging

Full action tracking for compliance and debugging.

```bash
# View today's logs
cat Logs\2026-03-05.jsonl

# View Ralph loop iterations
cat Logs\ralph_task_*.log

# Export audit trail
python audit_export.py ..\ --output audit_trail.csv
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GOLD TIER ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Gmail   │  │ WhatsApp │  │ Facebook │  │   File   │       │
│  │ Watcher  │  │ Watcher  │  │ Watcher  │  │  Watcher │       │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘       │
│       │             │             │             │              │
│       └─────────────┼─────────────┼─────────────┘              │
│                     │             │                            │
│                     ▼             ▼                            │
│           ┌─────────────────┐  ┌──────────────┐                │
│           │  Needs_Action/  │  │   Odoo 19    │                │
│           └────────┬────────┘  │  (Docker)    │                │
│                    │           └──────────────┘                │
│                    │                                           │
│                    ▼                                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              QWEN CODE + Ralph Wiggum Loop               │ │
│  │  - Reads action files                                    │ │
│  │  - Creates plans for complex tasks                       │ │
│  │  - Iterates until complete (max 10 iterations)           │ │
│  │  - Requests approval for sensitive actions               │ │
│  │  - Integrates with Odoo for accounting                   │ │
│  └──────────────────────────────────────────────────────────┘ │
│                    │                                           │
│        ┌───────────┼───────────┬──────────────┐               │
│        ▼           ▼           ▼              ▼               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │ Pending  │ │ Approved │ │   Done   │ │ Briefings│         │
│  │ Approval │ │          │ │          │ │          │         │
│  └────┬─────┘ └────┬─────┘ └──────────┘ └──────────┘         │
│       │            │                                          │
│       │            ▼                                          │
│       │     ┌────────────────────────────────────┐            │
│       │     │         MCP SERVERS                │            │
│       │     │  ┌──────┐ ┌──────────┐ ┌────────┐ │            │
│       │     │  │Email │ │ Facebook │ │ Odoo   │ │            │
│       │     │  │ MCP  │ │   MCP    │ │  MCP   │ │            │
│       │     │  └──┬───┘ └────┬─────┘ └───┬────┘ │            │
│       │     └─────┼──────────┼───────────┼──────┘            │
│       │            │          │           │                   │
│       ▼            ▼          ▼           ▼                   │
│  ┌──────────────────────────────────────────────────┐         │
│  │              EXTERNAL ACTIONS                    │         │
│  │  - Send Email    - Post to Facebook              │         │
│  │  - Create Invoice - Register Payment (Odoo)     │         │
│  │  - Generate Report - CEO Briefing               │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────┐         │
│  │           AUDIT LOGGING & MONITORING             │         │
│  │  - All actions logged to /Logs/*.jsonl           │         │
│  │  - Ralph iterations logged                       │         │
│  │  - Watchdog monitors process health              │         │
│  └──────────────────────────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md                  # Real-time status
├── Company_Handbook.md           # Rules & approval thresholds
├── Business_Goals.md             # Goals & metrics
├── README_GOLD_TIER.md           # This file
├── Inbox/                        # Drop files here
├── Needs_Action/                 # Items to process
│   ├── EMAIL_*.md               # Gmail emails
│   ├── WHATSAPP_*.md            # WhatsApp messages
│   ├── FACEBOOK_*.md            # Facebook notifications
│   └── FILE_*.md                # Dropped files
├── In_Progress/
│   └── gold_tier/               # Claimed tasks
├── Plans/                        # Multi-step task plans
│   ├── PLAN_*.md                # Task plans
│   └── STATE_*.json             # Ralph loop state
├── Pending_Approval/             # Awaiting human decision
├── Approved/                     # Approved, ready to execute
├── Rejected/                     # Rejected actions
├── Done/                         # Completed items
├── Accounting/                   # Transactions
├── Briefings/                    # CEO briefings
│   └── YYYY-MM-DD_Monday_Briefing.md
├── Logs/                         # Action logs
│   ├── YYYY-MM-DD.jsonl         # Daily logs
│   └── ralph_*.log              # Ralph iterations
├── Invoices/                     # Invoice templates
└── scripts/
    ├── base_watcher.py           # Base watcher class
    ├── filesystem_watcher.py     # File system monitor
    ├── gmail_watcher.py          # Gmail monitor
    ├── whatsapp_watcher.py       # WhatsApp monitor
    ├── facebook_watcher.py       # Facebook monitor (NEW)
    ├── orchestrator.py           # Main orchestration
    ├── ralph_wiggum_loop.py      # Ralph loop (NEW)
    ├── ceo_briefing_generator.py # CEO briefing (NEW)
    ├── approval_manager.py       # Approval workflow
    ├── email_mcp_server.py       # Email sending
    ├── linkedin_poster.py        # LinkedIn posting
    ├── odoo_mcp_server.py        # Odoo integration (NEW)
    ├── facebook_mcp_server.py    # Facebook integration (NEW)
    ├── requirements_gold.txt     # Gold tier dependencies
    └── start_all.bat             # Windows starter
```

## Approval Thresholds (Gold Tier)

Configure in `Company_Handbook.md`:

| Action Type | Auto-Approve | Requires Approval |
|-------------|--------------|-------------------|
| Email to known contact | Yes | No |
| Email to new contact | No | Yes |
| Email with attachment | No | Yes |
| Payment < $50 (via Odoo) | Yes | No |
| Payment ≥ $50 (via Odoo) | No | Yes |
| New partner in Odoo | No | Yes |
| Facebook post | No | Yes (always) |
| LinkedIn post | No | Yes (always) |
| File delete | No | Yes (always) |
| Invoice creation | Yes | No |
| Invoice send | No | Yes |

## Usage Examples

### Example 1: Process Invoice Request with Odoo

1. **Gmail Watcher** detects email: "Please send invoice for January consulting"
2. Creates `EMAIL_*.md` in `Needs_Action/`
3. **Ralph Loop** processes:
   - Reads email, identifies client
   - Creates invoice in Odoo via MCP
   - Generates PDF invoice
   - Creates approval file for email send
4. **You** approve by moving to `Approved`
5. **Email MCP** sends invoice
6. Action moved to `Done`, logged in Odoo

### Example 2: Facebook Post for Product Launch

1. Drop file `facebook_launch.txt` in `Inbox`
2. **File Watcher** creates action file
3. **Ralph Loop**:
   - Generates post content
   - Creates approval file
4. **You** approve
5. **Facebook MCP** posts update
6. Screenshot saved to `Done`

### Example 3: Weekly CEO Briefing

```bash
# Scheduled every Monday at 7 AM
python ceo_briefing_generator.py ..\

# Briefing includes:
# - Revenue from Odoo (last week)
# - Completed tasks from /Done
# - Bottlenecks from /Plans
# - Proactive suggestions
# - Action items for your review
```

### Example 4: Multi-Step Project with Ralph Loop

```bash
# Complex task: "Process all pending items and prepare monthly report"
python ralph_wiggum_loop.py ..\ ^
  --prompt "Process all files in Needs_Action, create invoices in Odoo for pending requests, and generate monthly report" ^
  --max-iterations 15 ^
  -v

# Ralph will:
# 1. Process each file in Needs_Action
# 2. Create Odoo invoices where needed
# 3. Request approvals for sensitive actions
# 4. Wait for your approval
# 5. Continue until all tasks complete
# 6. Generate monthly report
```

## Scheduled Tasks (Windows)

### Daily Briefing - 7:00 AM

```powershell
# Creates daily briefing from previous day's activity
python ceo_briefing_generator.py ..\
```

### Weekly CEO Briefing - Monday 7:00 AM

```powershell
# Comprehensive weekly report
python ceo_briefing_generator.py ..\
```

### Continuous Watchers - At Log On

```powershell
# Runs all watchers in background
python ralph_wiggum_loop.py ..\ --orchestrator --interval 30
```

### Odoo Health Check - Every Hour

```powershell
# Check Odoo is running
docker-compose ps
```

## Configuration

### Odoo Configuration

Edit `odoo/odoo-config/odoo.conf`:

```ini
[options]
admin_passwd = admin
db_host = db
db_port = 5432
db_user = odoo
db_password = odoo
external_api_url = http://localhost:8069
external_api_key = gold-tier-api-key-2026
```

### Facebook Configuration

```bash
# Session saved automatically after login
# Location: %USERPROFILE%\.facebook_session

# To re-authenticate:
python facebook_watcher.py ..\ --login
```

### Ralph Loop Configuration

```python
# In ralph_wiggum_loop.py
max_iterations = 10  # Max Claude iterations per task
approval_timeout = 24  # Hours to wait for approval
check_interval = 30  # Seconds between checks
```

## Troubleshooting

### Odoo Issues

| Issue | Solution |
|-------|----------|
| Container won't start | `docker-compose down && docker-compose up -d` |
| Can't access web UI | Wait 2-3 minutes for initialization |
| API authentication fails | Check credentials in odoo_mcp_server.py |
| Database error | `docker-compose logs db` |

### Facebook Issues

| Issue | Solution |
|-------|----------|
| Login fails | Re-authenticate with --login flag |
| Post button not found | Facebook UI changed, update selectors |
| Session expired | Re-run facebook_watcher.py --login |
| Account restricted | Stop automation, review Facebook ToS |

### Ralph Loop Issues

| Issue | Solution |
|-------|----------|
| Stuck in loop | Check logs for error, reduce max_iterations |
| Not completing tasks | Review approval files in Pending_Approval |
| High token usage | Optimize prompts, reduce iterations |

### CEO Briefing Issues

| Issue | Solution |
|-------|----------|
| No revenue data | Check Odoo connection or accounting files |
| Missing tasks | Verify files moved to Done folder |
| Wrong week dates | Use --week-start and --week-end flags |

## Security Notes

⚠️ **Important:**

1. **Never commit** credentials, tokens, or `.env` files to git
2. **Odoo default password**: Change admin password after first login!
3. **Facebook automation**: May violate ToS - use at own risk
4. **Store secrets** in environment variables or Windows Credential Manager
5. **Use app-specific passwords** if 2FA enabled
6. **Rotate credentials** regularly
7. **Review audit logs** in `/Logs` weekly
8. **Docker security**: Don't expose Odoo to public internet without HTTPS

## Monitoring

### Check System Status

```bash
# View dashboard
cat Dashboard.md

# Check Odoo status
docker-compose ps

# Check pending approvals
python approval_manager.py ..\ --list

# View Ralph loop state
cat Plans\STATE_*.json

# View recent logs
cat Logs\*-main.jsonl | Select-Object -Last 50
```

### Health Check Script

Create `health_check_gold.ps1`:

```powershell
Write-Host "AI Employee Gold Tier Health Check"
Write-Host "=================================="

# Check Docker (Odoo)
$odoo = docker-compose ps | Select-String "odoo"
if ($odoo -match "Up") {
    Write-Host "✓ Odoo running" -ForegroundColor Green
} else {
    Write-Host "✗ Odoo NOT running" -ForegroundColor Red
}

# Check watchers
$watchers = @("facebook_watcher", "gmail_watcher", "whatsapp_watcher")
foreach ($w in $watchers) {
    $process = Get-Process -Name "python" -ErrorAction SilentlyContinue |
               Where-Object {$_.CommandLine -like "*$w*"}
    if ($process) {
        Write-Host "✓ $w running" -ForegroundColor Green
    } else {
        Write-Host "✗ $w NOT running" -ForegroundColor Red
    }
}

# Check pending approvals
$pending = (Get-ChildItem "Pending_Approval\*.md" -ErrorAction SilentlyContinue).Count
Write-Host ""
Write-Host "Pending approvals: $pending"

# Check Ralph loop state
$states = Get-ChildItem "Plans\STATE_*.json" -ErrorAction SilentlyContinue
if ($states) {
    Write-Host "Active Ralph tasks: $($states.Count)"
}
```

## Performance Optimization

### Reduce Token Usage

1. **Optimize prompts**: Be specific and concise
2. **Limit iterations**: Set appropriate `--max-iterations`
3. **Cache results**: Store API responses in vault
4. **Batch operations**: Process multiple items in one Claude call

### Improve Response Time

1. **Reduce check interval**: Balance between responsiveness and resource usage
2. **Parallel watchers**: Run watchers in separate processes
3. **Use Odoo workers**: Configure in docker-compose.yml

## Gold Tier Completion Checklist

- [x] Odoo 19.0 Docker Compose setup
- [x] Odoo MCP server with accounting tools
- [x] Facebook watcher and MCP server
- [x] Ralph Wiggum loop implementation
- [x] CEO briefing generator
- [x] Error recovery and retry logic
- [x] Comprehensive audit logging
- [x] Gold Tier documentation

## Next Steps (Platinum Tier)

To upgrade to Platinum Tier:
- [ ] Deploy to cloud VM (Oracle/AWS) for 24/7 operation
- [ ] Implement Cloud/Local split architecture
- [ ] Add Twitter (X) integration
- [ ] Implement vault sync (Git/Syncthing)
- [ ] Add A2A (Agent-to-Agent) communication
- [ ] Deploy Odoo to cloud with HTTPS
- [ ] Implement work-zone specialization

## Resources

- [Hackathon Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Silver Tier README](README_SILVER_TIER.md)
- [Odoo Documentation](https://www.odoo.com/documentation)
- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- [MCP Specification](https://modelcontextprotocol.io)
- [Facebook Watcher Skill](../.qwen/skills/facebook-watcher/SKILL.md) (create)
- [Odoo MCP Skill](../.qwen/skills/odoo-mcp/SKILL.md) (create)

---

*AI Employee v0.3 (Gold Tier) - Built for Personal AI Employee Hackathon 0*
