# Personal AI Employee (Digital FTE)

A comprehensive blueprint for building an autonomous AI employee that manages personal and business affairs 24/7. This project transforms AI from a chatbot into a proactive business partner using **Claude Code** as the reasoning engine and **Obsidian** as the dashboard/memory.

## Project Overview

**Purpose:** Build a "Digital FTE" (Full-Time Equivalent) - an AI agent that works 168 hours/week at a fraction of human cost, managing:
- **Personal Affairs:** Gmail, WhatsApp, Bank transactions
- **Business Operations:** Social Media, Payments, Project Tasks, Accounting

**Architecture:** Local-first, agent-driven, human-in-the-loop

### Core Components

| Component | Role | Technology |
|-----------|------|------------|
| **The Brain** | Reasoning engine | Claude Code |
| **The Memory/GUI** | Dashboard & long-term memory | Obsidian (Markdown) |
| **The Senses** | Watchers monitoring inputs | Python scripts |
| **The Hands** | External system actions | MCP Servers |

### Key Patterns

1. **Watcher Architecture:** Lightweight Python scripts monitor Gmail, WhatsApp, filesystems, and trigger Claude when action is needed
2. **Ralph Wiggum Loop:** A Stop hook pattern that keeps Claude iterating until multi-step tasks are complete
3. **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
4. **File-Based Communication:** Agents communicate by writing files to `/Needs_Action/`, `/Plans/`, `/Done/`

## Directory Structure

```
YT-Personal-AI-Employe-FTEs/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json          # Skill dependencies
├── .qwen/skills/
│   └── browsing-with-playwright/   # Browser automation skill
│       ├── SKILL.md                 # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool reference
│       └── scripts/
│           ├── mcp-client.py        # Universal MCP client (HTTP/stdio)
│           ├── start-server.sh      # Start Playwright MCP server
│           ├── stop-server.sh       # Stop Playwright MCP server
│           └── verify.py            # Server health check
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| [Claude Code](https://claude.com/product/claude-code) | Active subscription | Primary reasoning engine |
| [Obsidian](https://obsidian.md/download) | v1.10.6+ | Knowledge base & dashboard |
| [Python](https://www.python.org/downloads/) | 3.13+ | Watcher scripts & orchestration |
| [Node.js](https://nodejs.org/) | v24+ LTS | MCP servers & automation |

### Hardware Requirements

- **Minimum:** 8GB RAM, 4-core CPU, 20GB free disk
- **Recommended:** 16GB RAM, 8-core CPU, SSD storage
- **For always-on:** Dedicated mini-PC or cloud VM

### Setup Checklist

```bash
# 1. Create Obsidian vault
mkdir AI_Employee_Vault
cd AI_Employee_Vault
mkdir -p Inbox Needs_Action Done Pending_Approval Approved Plans Accounting Briefings

# 2. Verify Claude Code
claude --version

# 3. Install Playwright (for browser automation)
npm install -g @playwright/mcp

# 4. Start Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# 5. Verify server
python3 .qwen/skills/browsing-with-playwright/scripts/verify.py
```

### Key Commands

#### Playwright MCP Server (Browser Automation)

```bash
# Start server (shared browser context for stateful sessions)
npx @playwright/mcp@latest --port 8808 --shared-browser-context &

# Stop server
bash scripts/stop-server.sh

# Verify running
python3 scripts/verify.py
```

#### MCP Client Operations

```bash
# List available tools
python3 mcp-client.py list -u http://localhost:8808

# Navigate to URL
python3 mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Take page snapshot (accessibility tree)
python3 mcp-client.py call -u http://localhost:8808 -t browser_snapshot -p '{}'

# Click element
python3 mcp-client.py call -u http://localhost:8808 -t browser_click \
  -p '{"element": "Submit button", "ref": "e42"}'

# Type text
python3 mcp-client.py call -u http://localhost:8808 -t browser_type \
  -p '{"element": "Search input", "ref": "e15", "text": "hello", "submit": true}'

# Execute JavaScript
python3 mcp-client.py call -u http://localhost:8808 -t browser_evaluate \
  -p '{"function": "return document.title"}'
```

## Development Conventions

### File Organization (Obsidian Vault)

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items |
| `/Needs_Action` | Items requiring processing |
| `/In_Progress/<agent>/` | Claimed items (prevents double-work) |
| `/Pending_Approval` | Actions awaiting human approval |
| `/Approved` | Approved actions ready for execution |
| `/Done` | Completed items |
| `/Plans` | Multi-step task plans |
| `/Accounting` | Bank transactions, invoices |
| `/Briefings` | CEO briefings, weekly reports |

### Watcher Script Pattern

All watchers follow the `BaseWatcher` abstract class:

```python
from pathlib import Path
from abc import ABC, abstractmethod

class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval

    @abstractmethod
    def check_for_updates(self) -> list:
        '''Return list of new items to process'''
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        '''Create .md file in Needs_Action folder'''
        pass

    def run(self):
        while True:
            items = self.check_for_updates()
            for item in items:
                self.create_action_file(item)
            time.sleep(self.check_interval)
```

### Action File Schema

```markdown
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-01-07T10:30:00Z
priority: high
status: pending
---

## Email Content
{message_body}

## Suggested Actions
- [ ] Reply to sender
- [ ] Create invoice
- [ ] Archive after processing
```

### Approval Request Schema

For sensitive actions (payments, sending messages):

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
created: 2026-01-07T10:30:00Z
expires: 2026-01-08T10:30:00Z
status: pending
---

## Payment Details
- Amount: $500.00
- To: Client A (Bank: XXXX1234)
- Reference: Invoice #1234

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder.
```

## Available Skills

### browsing-with-playwright

Browser automation via Playwright MCP server. Use for:
- Web scraping and data extraction
- Form submission and UI testing
- Social media posting automation
- Payment portal interactions

**Server Location:** `http://localhost:8808`

**Key Tools:**
- `browser_navigate` - Navigate to URL
- `browser_snapshot` - Get accessibility snapshot (element refs)
- `browser_click` - Click element by ref
- `browser_type` - Type text into element
- `browser_fill_form` - Fill multiple fields
- `browser_take_screenshot` - Capture screenshot
- `browser_evaluate` - Execute JavaScript
- `browser_run_code` - Run multi-step Playwright code
- `browser_wait_for` - Wait for text/time

## MCP Servers

| Server | Capabilities | Use Case |
|--------|--------------|----------|
| `filesystem` | Read, write, list files | Built-in for vault access |
| `email-mcp` | Send, draft, search emails | Gmail integration |
| `browser-mcp` | Navigate, click, fill forms | Web automation |
| `calendar-mcp` | Create, update events | Scheduling |

Configure in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp"],
      "env": {"HEADLESS": "true"}
    }
  ]
}
```

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12 hrs | Dashboard.md, 1 Watcher, basic folder structure |
| **Silver** | 20-30 hrs | 2+ Watchers, Plan.md generation, 1 MCP server, HITL workflow |
| **Gold** | 40+ hrs | Full integration, Odoo accounting, social media, Ralph Wiggum loop |
| **Platinum** | 60+ hrs | Cloud deployment, Cloud/Local split, 24/7 always-on operation |

## Key Resources

- **Main Blueprint:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Ralph Wiggum Pattern:** [GitHub Reference](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum)
- **Agent Skills:** [Claude Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- **MCP Servers:** [Model Context Protocol](https://github.com/AlanOgic/mcp-odoo-adv)

## Weekly Research Meeting

**When:** Wednesdays at 10:00 PM PKT
**Zoom:** [Join Meeting](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- Meeting ID: 871 8870 7642
- Passcode: 744832

**Archive:** [YouTube Channel](https://www.youtube.com/@panaversity)
