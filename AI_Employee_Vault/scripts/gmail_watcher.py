#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitor Gmail for new important/unread emails.

Creates action files in Obsidian vault's /Needs_Action folder.

Usage:
    python gmail_watcher.py /path/to/vault --authenticate  # First time only
    python gmail_watcher.py /path/to/vault                 # Run watcher
"""

import sys
import time
import logging
import base64
import pickle
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional, List

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Import base watcher from same directory
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """Monitor Gmail for new important/unread emails."""
    
    def __init__(self, vault_path: str, credentials_path: str, token_path: str, 
                 check_interval: int = 120, keywords: List[str] = None,
                 require_keywords: bool = False):
        super().__init__(vault_path, check_interval)
        
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.keywords = keywords or ['urgent', 'invoice', 'payment', 'asap']
        self.require_keywords = require_keywords  # If False, get ALL unread emails
        self.service: Optional[build] = None
        self.processed_ids = set()
        
        # Load previously processed IDs from cache
        self._load_processed_ids()
    
    def _load_processed_ids(self):
        """Load processed email IDs from cache file."""
        cache_file = self.vault_path / '.gmail_cache.pkl'
        self.logger.info(f"Cache file location: {cache_file}")
        self.logger.info(f"Cache file exists: {cache_file.exists()}")
        
        if cache_file.exists():
            try:
                self.processed_ids = pickle.loads(cache_file.read_bytes())
                self.logger.info(f"Loaded {len(self.processed_ids)} processed email IDs from cache")
            except Exception as e:
                self.logger.warning(f"Could not load cache: {e}")
        else:
            self.logger.info("No cache file found - will process all emails")
    
    def _save_processed_ids(self):
        """Save processed email IDs to cache file."""
        cache_file = self.vault_path / '.gmail_cache.pkl'
        try:
            # Keep only last 1000 IDs
            if len(self.processed_ids) > 1000:
                self.processed_ids = set(list(self.processed_ids)[-1000:])
            cache_file.write_bytes(pickle.dumps(self.processed_ids))
        except Exception as e:
            self.logger.warning(f"Could not save cache: {e}")
    
    def authenticate(self) -> bool:
        """Run OAuth authentication flow."""
        if not self.credentials_path.exists():
            self.logger.error(f"Credentials file not found: {self.credentials_path}")
            return False
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path,
                scopes=SCOPES
            )
            creds = flow.run_local_server(port=0)
            
            # Save token
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'wb') as f:
                pickle.dump(creds, f)
            
            self.logger.info("Authentication successful!")
            self.logger.info(f"Token saved to: {self.token_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            return False
    
    def get_service(self) -> Optional[build]:
        """Get authenticated Gmail API service."""
        if not self.token_path.exists():
            self.logger.error("Token not found. Run with --authenticate first.")
            return None
        
        try:
            creds = pickle.loads(self.token_path.read_bytes())
            
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(None)
                    with open(self.token_path, 'w') as f:
                        pickle.dump(creds, f)
                else:
                    self.logger.error("Credentials invalid. Re-authenticate.")
                    return None
            
            return build('gmail', 'v1', credentials=creds)
            
        except Exception as e:
            self.logger.error(f"Error getting service: {e}")
            return None
    
    def check_for_updates(self) -> list:
        """Fetch unread emails from Gmail."""
        if not self.service:
            self.service = self.get_service()
        
        if not self.service:
            return []
        
        try:
            # Build query
            # If require_keywords is False, just get all unread emails
            # If require_keywords is True, filter by keywords
            if self.require_keywords and self.keywords:
                keyword_query = ' OR '.join([f'"{kw}"' for kw in self.keywords])
                query = f'is:unread ({keyword_query})'
            else:
                query = 'is:unread'
            
            self.logger.info(f"Gmail query: {query}")
            
            # Fetch messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            self.logger.info(f"Total messages from API: {len(messages)}")
            
            # Log message IDs
            for msg in messages:
                self.logger.info(f"  Message ID: {msg['id']}")
            
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]
            self.logger.info(f"New messages (not in cache): {len(new_messages)}")
            
            self.logger.info(f"Found {len(new_messages)} new emails")
            return new_messages
            
        except HttpError as e:
            self.logger.error(f"Gmail API error: {e}")
            if e.resp.status == 401:
                self.service = None
            return []
        except Exception as e:
            self.logger.error(f"Error checking emails: {e}")
            return []
    
    def create_action_file(self, message) -> Path:
        """Create markdown action file for email."""
        try:
            msg = self.service.users().messages().get(
                userId='me', id=message['id'], format='full'
            ).execute()
            
            # Extract headers
            headers = {h['name']: h['value'] for h in msg['payload']['headers']}
            
            # Get body
            body = self._extract_body(msg['payload'])
            
            # Get attachments info
            attachments = self._get_attachments_info(msg['payload'])
            
            # Determine priority
            priority = self._determine_priority(headers.get('Subject', ''), body)
            
            content = f'''---
type: email
from: {headers.get('From', 'Unknown')}
to: {headers.get('To', '')}
subject: {headers.get('Subject', 'No Subject')}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
message_id: {message['id']}
---

# Email Content

**From:** {headers.get('From', 'Unknown')}  
**To:** {headers.get('To', '')}  
**Subject:** {headers.get('Subject', 'No Subject')}  
**Date:** {headers.get('Date', '')}

---

{body if body else '*No text content*'}

---

# Attachments
{self._format_attachments(attachments) if attachments else '*No attachments*'}

# Suggested Actions
- [ ] Review email content
- [ ] Reply to sender
- [ ] Take required action
- [ ] Archive after processing

---
*Generated by Gmail Watcher v0.1 (Silver Tier)*
'''
            filepath = self.needs_action / f'EMAIL_{message["id"]}.md'
            filepath.write_text(content)
            
            self.processed_ids.add(message['id'])
            self._save_processed_ids()
            
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            raise
    
    def _extract_body(self, payload) -> str:
        """Extract email body from payload."""
        body_parts = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part.get('body', {}):
                        data = part['body']['data']
                        body_parts.append(base64.urlsafe_b64decode(data).decode('utf-8'))
        
        return '\n\n'.join(body_parts) if body_parts else ""
    
    def _get_attachments_info(self, payload) -> list:
        """Get attachment information from payload."""
        attachments = []
        
        if 'parts' in payload:
            for part in payload['parts']:
                if part['filename']:
                    attachments.append({
                        'filename': part['filename'],
                        'size': part['body'].get('size', 0),
                        'mime_type': part['mimeType']
                    })
        
        return attachments
    
    def _format_attachments(self, attachments: list) -> str:
        """Format attachments as markdown list."""
        lines = []
        for att in attachments:
            size_kb = att['size'] / 1024
            lines.append(f"- {att['filename']} ({size_kb:.1f} KB)")
        return '\n'.join(lines)
    
    def _determine_priority(self, subject: str, body: str) -> str:
        """Determine email priority based on content."""
        high_priority_keywords = ['urgent', 'asap', 'immediately', 'emergency']
        medium_priority_keywords = ['invoice', 'payment', 'deadline', 'review']
        
        text = (subject + ' ' + body).lower()
        
        if any(kw in text for kw in high_priority_keywords):
            return 'high'
        elif any(kw in text for kw in medium_priority_keywords):
            return 'medium'
        return 'normal'
    
    def run(self):
        """Main loop - continuously check for new emails."""
        self.logger.info('=' * 50)
        self.logger.info('Gmail Watcher starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Credentials: {self.credentials_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info('=' * 50)
        
        # Check authentication
        if not self.get_service():
            self.logger.error("Failed to authenticate. Exiting.")
            return
        
        super().run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gmail Watcher - Monitor Gmail for new emails')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--credentials', '-c', 
                       help='Path to OAuth credentials JSON (default: ./credentials.json)')
    parser.add_argument('--token', '-t',
                       help='Path to token file (default: vault/.gmail_token.pkl)')
    parser.add_argument('--interval', '-i', type=int, default=120,
                       help='Check interval in seconds (default: 120)')
    parser.add_argument('--keywords', '-k', nargs='+',
                       help='Keywords to filter emails')
    parser.add_argument('--authenticate', '-a', action='store_true',
                       help='Run authentication flow')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Default paths
    if args.credentials:
        credentials_path = Path(args.credentials)
    else:
        # Look for credentials.json in current directory
        credentials_path = Path.cwd() / 'credentials.json'
    
    if args.token:
        token_path = Path(args.token)
    else:
        token_path = vault_path / '.gmail_token.pkl'
    
    # Check credentials exist
    if not credentials_path.exists():
        print(f"Error: Credentials file not found: {credentials_path}")
        print("\nTo get credentials:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create a project and enable Gmail API")
        print("3. Create OAuth credentials (Desktop app)")
        print("4. Download and save as credentials.json")
        sys.exit(1)
    
    # Create watcher
    watcher = GmailWatcher(
        str(vault_path),
        str(credentials_path),
        str(token_path),
        args.interval or 120,
        args.keywords
    )
    
    if args.authenticate:
        print("Starting Gmail authentication...")
        print("A browser window will open. Sign in with your Google account.")
        print("Grant permissions when prompted.")
        print()
        if watcher.authenticate():
            print("")
            print("Authentication successful!")
            print("You can now run the watcher without --authenticate")
            print("")
            print("Example:")
            print(f"  python gmail_watcher.py {vault_path}")
        else:
            print("")
            print("Authentication failed")
            sys.exit(1)
    else:
        watcher.run()


if __name__ == '__main__':
    main()
