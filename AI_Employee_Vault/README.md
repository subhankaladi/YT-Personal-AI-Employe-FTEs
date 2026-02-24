# AI Employee - Bronze Tier

A local-first autonomous AI agent that manages personal and business affairs using **Qwen Code** as the reasoning engine and **Obsidian** as the dashboard/memory.

This is the **Bronze Tier** implementation containing:
- ✅ Obsidian vault with Dashboard.md and Company_Handbook.md
- ✅ File System Watcher script (monitors Inbox folder)
- ✅ Orchestrator to trigger Qwen Code
- ✅ Basic folder structure: /Inbox, /Needs_Action, /Done, /Pending_Approval, /Approved

## Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Qwen Code](https://github.com/QwenLM/Qwen) | Latest | Reasoning engine |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Dashboard (optional for viewing) |

### Installation

1. **Install Python dependencies:**

```bash
cd AI_Employee_Vault/scripts
pip install -r requirements.txt
```

2. **Verify Qwen Code is installed:**

```bash
qwen --version
```

3. **Open the vault in Obsidian (optional but recommended):**

```
File → Open Folder → Select AI_Employee_Vault
```

### Running the AI Employee

#### Option 1: Windows (using batch script)

```bash
cd AI_Employee_Vault\scripts
start.bat
```

#### Option 2: Cross-platform (manual)

```bash
cd AI_Employee_Vault

# Terminal 1: Start the File System Watcher
python scripts/filesystem_watcher.py ./AI_Employee_Vault

# Terminal 2: Start the Orchestrator
python scripts/orchestrator.py ./AI_Employee_Vault --interval 30
```

## How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR COMPUTER                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────────────────────┐  │
│  │  Inbox/     │─────▶│   File System Watcher       │  │
│  │ (drop files │      │   (Python + watchdog)       │  │
│  │   here)     │      └──────────────┬──────────────┘  │
│  └─────────────┘                     │                 │
│                                      ▼                 │
│                            ┌──────────────────┐        │
│                            │  Needs_Action/   │        │
│                            │  (action files)  │        │
│                            └────────┬─────────┘        │
│                                     │                  │
│                                     ▼                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │              QWEN CODE                          │   │
│  │    Reads action files + Company Handbook       │   │
│  │    Creates plans, requests approval            │   │
│  └─────────────────────────────────────────────────┘   │
│                                     │                  │
│                                     ▼                  │
│                            ┌──────────────────┐        │
│                            │  Pending_Approval│        │
│                            │  (awaiting you)  │        │
│                            └────────┬─────────┘        │
│                                     │                  │
│                          You move to /Approved         │
│                                     │                  │
│                                     ▼                  │
│                            ┌──────────────────┐        │
│                            │    QWEN CODE      │        │
│                            │  (executes action)│        │
│                            └────────┬─────────┘        │
│                                     │                  │
│                                     ▼                  │
│                            ┌──────────────────┐        │
│                            │      Done/       │        │
│                            │   (completed)    │        │
│                            └──────────────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Workflow Example

1. **Drop a file** into `AI_Employee_Vault/Inbox/`
   - Any file: email export, document, note, etc.

2. **File System Watcher detects it** and:
   - Copies file to `Needs_Action/`
   - Creates metadata `.md` file with context

3. **Orchestrator triggers Qwen Code** to:
   - Read the action file
   - Read `Company_Handbook.md` for rules
   - Determine required actions
   - Create a `Plan.md` for multi-step tasks

4. **For sensitive actions**, Qwen creates approval request in `Pending_Approval/`

5. **You review** and move file to `Approved/` or `Rejected/`

6. **Qwen executes** approved actions and moves to `Done/`

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md              # Real-time status dashboard
├── Company_Handbook.md       # Rules of engagement
├── Business_Goals.md         # Goals and metrics
├── Inbox/                    # Drop files here
├── Needs_Action/             # Items pending processing
├── Plans/                    # Multi-step task plans
├── Pending_Approval/         # Awaiting your approval
├── Approved/                 # Approved, ready to execute
├── Rejected/                 # Rejected actions
├── Done/                     # Completed items
├── Accounting/               # Transactions, invoices
├── Briefings/                # CEO briefings (weekly)
├── Logs/                     # Action logs
├── Invoices/                 # Invoice templates
├── In_Progress/              # Currently being worked on
└── scripts/
    ├── base_watcher.py       # Abstract watcher class
    ├── filesystem_watcher.py # File system monitor
    ├── orchestrator.py       # Main orchestration
    ├── requirements.txt      # Python dependencies
    └── start.bat             # Windows starter
```

## Sample Action Files

Sample files are included for testing:

| File | Purpose |
|------|---------|
| `Needs_Action/SAMPLE_EMAIL_invoice_request.md` | Sample email action |
| `Needs_Action/SAMPLE_FILE_contract_review.md` | Sample file drop action |
| `Pending_Approval/SAMPLE_EMAIL_send_invoice.md` | Sample approval request |
| `Plans/SAMPLE_PLAN_invoice_client_a.md` | Sample multi-step plan |

**Delete sample files after testing.**

## Using with Qwen Code

### Manual Processing

To manually process pending items:

```bash
cd AI_Employee_Vault
qwen "Process all files in Needs_Action folder. Read Company_Handbook.md for rules. Create plans for multi-step tasks. Move completed items to Done."
```

### Automated Processing

The orchestrator automatically triggers Qwen Code every 30 seconds. Adjust with:

```bash
python scripts/orchestrator.py ./AI_Employee_Vault --interval 60
```

## Customization

### Modify Rules

Edit `Company_Handbook.md` to change:
- Approval thresholds
- Response time expectations
- Communication style
- Working hours

### Add New Watchers

Extend `base_watcher.py` to create:
- Gmail Watcher (using Gmail API)
- WhatsApp Watcher (using Playwright)
- Finance Watcher (using bank APIs)

See the hackathon document for example implementations.

## Troubleshooting

### "Qwen Code not found"

Ensure Qwen Code is installed and in PATH. Check the installation instructions for your specific Qwen Code setup.

### "Module not found: watchdog"

Install Python dependencies:

```bash
pip install watchdog
```

### Watcher not detecting files

1. Ensure files are dropped in `Inbox/` folder
2. Check watcher is running (should see log output)
3. Verify file is not hidden or temp file

### Qwen Code hangs

Press `Ctrl+C` to interrupt and restart orchestrator.

## Next Steps (Silver Tier)

To upgrade to Silver Tier, add:
- [ ] Gmail Watcher (monitor incoming emails)
- [ ] WhatsApp Watcher (monitor messages)
- [ ] MCP server for sending emails
- [ ] Human-in-the-loop approval workflow
- [ ] Scheduled tasks (cron/Task Scheduler)
- [ ] LinkedIn auto-posting

## Security Notes

⚠️ **Important Security Practices:**

1. **Never commit** the vault to public git
2. **Add to .gitignore:**
   ```
   Logs/
   Accounting/
   *.env
   ```
3. **Use environment variables** for API keys
4. **Review all approval requests** before approving
5. **Start in dry-run mode** when testing new watchers

## Resources

- [Hackathon Document](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://github.com/QwenLM/Qwen)
- [Obsidian Help](https://help.obsidian.md)
- [Watchdog Docs](https://pythonhosted.org/watchdog/)

---

*AI Employee v0.1 (Bronze Tier) - Built for Personal AI Employee Hackathon 0*
