---
name: email-mcp-server
description: |
  MCP server for sending emails via Gmail API. Provides tools for composing,
  drafting, and sending emails. Supports attachments, HTML content, and
  human-in-the-loop approval workflow for sensitive actions.
---

# Email MCP Server

Send emails via Gmail API using Model Context Protocol (MCP).

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create/select project
3. Enable **Gmail API**
4. Create OAuth credentials (Desktop app)
5. Download as `credentials.json`

### 2. Install Dependencies

```bash
npm install
# or
pip install -r requirements.txt
```

### 3. Authenticate

```bash
python email_mcp_server.py --authenticate
```

## Configuration

Create `config.json`:

```json
{
  "credentials_path": "C:\\Users\\YourName\\credentials.json",
  "token_path": "C:\\Users\\YourName\\token.json",
  "sender_name": "Your Name",
  "sender_email": "you@example.com",
  "dry_run": false,
  "require_approval": true,
  "approval_threshold": "new_contacts"
}
```

## Tools

### `email_send`

Send an email immediately.

**Parameters:**
- `to` (string): Recipient email address
- `subject` (string): Email subject
- `body` (string): Email body (plain text or HTML)
- `cc` (string[], optional): CC recipients
- `bcc` (string[], optional): BCC recipients
- `attachments` (string[], optional): File paths to attach

**Example:**
```json
{
  "to": "client@example.com",
  "subject": "Invoice #001 - January 2026",
  "body": "Please find attached your invoice...",
  "attachments": ["/path/to/invoice.pdf"]
}
```

### `email_draft`

Create a draft email (does not send).

**Parameters:** Same as `email_send`

**Returns:** Draft ID for later review/send

### `email_search`

Search emails in Gmail.

**Parameters:**
- `query` (string): Gmail search query
- `max_results` (number): Maximum results (default: 10)

**Example:**
```json
{
  "query": "from:client@example.com is:unread",
  "max_results": 5
}
```

### `email_reply`

Reply to an existing email.

**Parameters:**
- `message_id` (string): Original message ID
- `body` (string): Reply body
- `include_original` (boolean): Include original message (default: true)

## Usage

### Start Server

```bash
# Node.js version
node index.js

# Python version
python email_mcp_server.py
```

### Configure in Qwen Code

Add to `~/.config/qwen-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "python",
      "args": ["/path/to/email_mcp_server.py"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    }
  ]
}
```

### Use in Qwen Code

```
qwen "Send an email to client@example.com with subject 'Meeting Tomorrow' and body 'Looking forward to our meeting at 2pm.'"
```

## Human-in-the-Loop Workflow

For sensitive actions, the server supports approval workflow:

1. **Check recipient**: If new contact or over threshold
2. **Create approval file**: `/Pending_Approval/EMAIL_send_*.md`
3. **Wait for approval**: User moves to `/Approved`
4. **Send email**: Orchestrator triggers send after approval

### Approval Thresholds

| Condition | Action |
|-----------|--------|
| New contact | Require approval |
| Bulk send (>5) | Require approval |
| Contains attachment | Require approval |
| Known contact, no attachment | Auto-send (optional) |

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│ Qwen Code   │────▶│ Email MCP    │────▶│ Gmail API   │
│             │     │ Server       │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │ Approval     │
                    │ Workflow     │
                    └──────────────┘
```

## Example Flow

### 1. Qwen Code Creates Plan

```markdown
---
type: plan
objective: Send invoice to Client A
---

# Steps
- [x] Generate invoice PDF
- [ ] Send email with attachment
  - Requires approval (new contact + attachment)
  - See: /Pending_Approval/EMAIL_send_invoice.md
```

### 2. Create Approval Request

```markdown
---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #001
created: 2026-02-24T10:30:00Z
---

# Email to Send

**To:** client@example.com  
**Subject:** Invoice #001  
**Attachment:** invoice.pdf

---
Move to /Approved to send, /Rejected to cancel.
```

### 3. User Approves

Move file from `/Pending_Approval` to `/Approved`

### 4. Orchestrator Executes

```bash
python mcp_client.py call -u http://localhost:8809 \
  -t email_send \
  -p '{"to": "client@example.com", "subject": "Invoice #001", ...}'
```

## Security Notes

- **Never commit** credentials or tokens
- **Use app-specific passwords** if 2FA enabled
- **Rotate credentials** regularly
- **Audit logs** for all sent emails
- **Rate limiting** to prevent abuse

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid credentials" | Re-authenticate with --authenticate |
| "Sending failed" | Check Gmail API quota, enable sending scope |
| "Attachment not found" | Verify file path is absolute |
| "Approval required" | Move approval file to /Approved |

## Code Example

```python
#!/usr/bin/env python3
"""Email MCP Server - Send emails via Gmail API."""

import json
import base64
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailMCPServer:
    def __init__(self, credentials_path: str, token_path: str):
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        
    def authenticate(self):
        """Run OAuth flow."""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path, scopes=SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open(self.token_path, 'w') as f:
            json.dump(pickle.dumps(creds).decode(), f)
        
    def get_service(self):
        """Get authenticated Gmail service."""
        creds = json.loads(self.token_path.read_text())
        return build('gmail', 'v1', credentials=creds)
    
    def send_email(self, to: str, subject: str, body: str, 
                   attachments: list = None, **kwargs):
        """Send an email."""
        if not self.service:
            self.service = self.get_service()
        
        # Create message
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        if attachments:
            for path in attachments:
                with open(path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={Path(path).name}')
                message.attach(part)
        
        # Encode and send
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = self.service.users().messages().send(
            userId='me', body={'raw': raw}
        ).execute()
        
        return {'id': result['id'], 'thread_id': result['threadId']}
```

## Next Steps

1. Set up approval workflow in orchestrator
2. Configure approval thresholds in config
3. Add email templates for common responses
4. Integrate with Gmail Watcher for reply threading
