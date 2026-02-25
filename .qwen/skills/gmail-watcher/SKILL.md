---
name: gmail-watcher
description: |
  Monitor Gmail for new important/unread emails and create action files in Obsidian vault.
  Uses Gmail API to fetch emails matching criteria (unread, important, from specific senders).
  Creates structured markdown files in /Needs_Action folder for AI processing.
---

# Gmail Watcher Skill

Monitor Gmail inbox and create actionable items for your AI Employee.

## Prerequisites

### 1. Enable Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable **Gmail API**:
   - Navigate to **APIs & Services** → **Library**
   - Search for "Gmail API" and enable it

### 2. Create OAuth Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. Application type: **Desktop app**
4. Download the credentials JSON file
5. Save as `credentials.json` in a secure location

### 3. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 4. First-Time Authentication

Run the watcher once to authenticate:

```bash
python gmail_watcher.py /path/to/vault --authenticate
```

This will open a browser window for OAuth consent.

## Configuration

Create a config file at `vault_path/scripts/gmail_config.json`:

```json
{
  "credentials_path": "C:\\Users\\YourName\\credentials.json",
  "token_path": "C:\\Users\\YourName\\token.json",
  "check_interval": 120,
  "keywords": ["urgent", "invoice", "payment", "asap"],
  "label_filter": "IMPORTANT",
  "max_results": 10
}
```

## Usage

### Basic Usage

```bash
python gmail_watcher.py /path/to/vault
```

### With Custom Config

```bash
python gmail_watcher.py /path/to/vault --config /path/to/config.json
```

### Authenticate First

```bash
python gmail_watcher.py /path/to/vault --authenticate
```

## Output Format

Creates markdown files in `/Needs_Action/`:

```markdown
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-02-24T10:30:00Z
priority: high
status: pending
message_id: 18d4f2a3b5c6e7f8
---

# Email Content

{email_body}

# Attachments
- invoice.pdf (25 KB)

# Suggested Actions
- [ ] Reply to sender
- [ ] Process invoice
- [ ] Archive after processing
```

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────────┐
│   Gmail     │────▶│ Gmail Watcher│────▶│ Needs_Action/    │
│   API       │     │   (Python)   │     │ EMAIL_*.md       │
└─────────────┘     └──────────────┘     └──────────────────┘
```

## Example: Full Workflow

1. **Watcher runs** every 2 minutes
2. **Fetches** unread, important emails
3. **Creates** action file in `/Needs_Action/`
4. **Orchestrator** triggers Qwen Code
5. **Qwen** reads email, creates plan, takes action

## Security Notes

- **Never commit** `credentials.json` or `token.json` to git
- Store credentials in secure location (not in vault)
- Use app-specific passwords if 2FA enabled
- Rotate credentials regularly

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid credentials" | Re-run with `--authenticate` flag |
| "Gmail API not enabled" | Enable Gmail API in Google Cloud Console |
| "Token expired" | Delete `token.json`, re-authenticate |
| No emails found | Check label filter, ensure emails are unread |

## Code Example

```python
from pathlib import Path
from base_watcher import BaseWatcher
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle

class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str, token_path: str):
        super().__init__(vault_path, check_interval=120)
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.service = None
        self.processed_ids = set()
        
    def authenticate(self):
        """Run OAuth flow and save token."""
        flow = InstalledAppFlow.from_client_secrets_file(
            self.credentials_path,
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )
        creds = flow.run_local_server(port=0)
        with open(self.token_path, 'w') as f:
            pickle.dump(creds, f)
        print("Authentication successful!")
        
    def get_service(self):
        """Get authenticated Gmail service."""
        if not self.token_path.exists():
            raise Exception("Token not found. Run with --authenticate first.")
        
        creds = pickle.loads(self.token_path.read_bytes())
        return build('gmail', 'v1', credentials=creds)
    
    def check_for_updates(self) -> list:
        """Fetch unread, important emails."""
        if not self.service:
            self.service = self.get_service()
        
        results = self.service.users().messages().list(
            userId='me',
            q='is:unread is:important',
            maxResults=10
        ).execute()
        
        messages = results.get('messages', [])
        return [m for m in messages if m['id'] not in self.processed_ids]
    
    def create_action_file(self, message) -> Path:
        """Create markdown action file for email."""
        msg = self.service.users().messages().get(
            userId='me', id=message['id'], format='full'
        ).execute()
        
        # Extract headers
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        
        # Get body
        body = self._extract_body(msg['payload'])
        
        content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: high
status: pending
message_id: {message['id']}
---

# Email Content

{body}

# Suggested Actions
- [ ] Reply to sender
- [ ] Take required action
- [ ] Archive after processing
'''
        filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
        filepath.write_text(content)
        self.processed_ids.add(message['id'])
        return filepath
    
    def _extract_body(self, payload) -> str:
        """Extract email body from payload."""
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    import base64
                    return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
        elif 'body' in payload:
            import base64
            return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
        return "No content"
```

## Next Steps

After setting up Gmail Watcher:
1. Configure orchestrator to process email action files
2. Set up Email MCP for sending replies
3. Create approval workflow for sensitive emails
4. Add filters for automatic categorization
