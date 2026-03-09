#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WhatsApp Watcher - Monitor WhatsApp Web for messages with keywords.

Creates action files in Obsidian vault's /Needs_Action folder.

WARNING: This uses WhatsApp Web automation which may violate WhatsApp's Terms of Service.
Use at your own risk and only for personal automation.

Usage:
    python whatsapp_watcher.py /path/to/vault
"""

import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

# Import base watcher from same directory
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class WhatsAppWatcher(BaseWatcher):
    """Monitor WhatsApp Web for messages containing keywords."""
    
    def __init__(self, vault_path: str, session_path: str,
                 keywords: List[str] = None, check_interval: int = 30,
                 quiet_hours: Dict[str, int] = None):
        """
        Initialize WhatsApp Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to save browser session
            keywords: Keywords to filter messages (default: urgent, asap, invoice, etc.)
            check_interval: Seconds between checks (default: 30)
            quiet_hours: Dict with 'start' and 'end' hour for quiet period
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path)
        self.keywords = keywords or ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing']
        self.quiet_hours = quiet_hours or {'start': 22, 'end': 6}
        self.processed_messages = set()
        
        # Ensure session path exists
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Keywords to monitor: {self.keywords}")
        self.logger.info(f"Quiet hours: {self.quiet_hours['start']}:00 - {self.quiet_hours['end']}:00")
    
    def is_quiet_hours(self) -> bool:
        """Check if current time is within quiet hours."""
        now = datetime.now().hour
        start = self.quiet_hours['start']
        end = self.quiet_hours['end']
        
        # Handle overnight quiet hours (e.g., 22:00 - 06:00)
        if start > end:
            return now >= start or now < end
        else:
            return start <= now < end
    
    def check_for_updates(self) -> list:
        """Check WhatsApp Web for new messages with keywords."""
        # Skip during quiet hours
        if self.is_quiet_hours():
            self.logger.debug("Quiet hours active - skipping check")
            return []
        
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch with persistent context (saves session/cookies)
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ],
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                self.logger.debug("Navigating to WhatsApp Web...")
                page.goto('https://web.whatsapp.com', wait_until='networkidle')
                
                # Wait for chat list to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                    self.logger.debug("Chat list loaded")
                except PlaywrightTimeout:
                    self.logger.warning("Chat list did not load - may need QR scan")
                    browser.close()
                    return []
                
                # Wait a bit for content to fully load
                time.sleep(2)
                
                # Find all chat items
                try:
                    chats = page.query_selector_all('[role="row"]')
                    self.logger.debug(f"Found {len(chats)} chats")
                    
                    for chat in chats:
                        try:
                            # Get chat text content
                            text = chat.inner_text(timeout=2000)
                            lines = text.split('\n')
                            
                            # Check if unread (aria-label contains "unread")
                            aria_label = chat.get_attribute('aria-label', timeout=1000) or ''
                            is_unread = 'unread' in aria_label.lower()
                            
                            # For demo, also check if first line looks like a name (short)
                            # and there's message content after
                            if len(lines) >= 2:
                                # Check for keywords in message
                                text_lower = text.lower()
                                matched_keywords = [kw for kw in self.keywords if kw in text_lower]
                                
                                if matched_keywords and is_unread:
                                    messages.append({
                                        'text': text,
                                        'aria_label': aria_label,
                                        'keywords': matched_keywords,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.logger.info(f"Found message with keywords: {matched_keywords}")
                        except Exception as e:
                            # Skip individual chat errors
                            continue
                    
                except Exception as e:
                    self.logger.error(f"Error finding chats: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error in WhatsApp check: {e}")
        
        # Filter out already processed messages
        new_messages = []
        for msg in messages:
            msg_hash = hash(msg['text'])
            if msg_hash not in self.processed_messages:
                new_messages.append(msg)
                self.processed_messages.add(msg_hash)
        
        self.logger.info(f"Found {len(new_messages)} new messages with keywords")
        return new_messages
    
    def create_action_file(self, message) -> Path:
        """Create markdown action file for WhatsApp message."""
        # Parse message content
        lines = message['text'].split('\n')
        
        # First line is usually the sender name
        sender = lines[0].strip() if lines else 'Unknown'
        
        # Rest is message content
        message_content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else 'No content'
        
        # Create unique filename
        timestamp = int(time.time() * 1000)
        filename = f'WHATSAPP_{timestamp}.md'
        
        content = f'''---
type: whatsapp_message
from: {self._sanitize_field(sender)}
received: {message['timestamp']}
priority: high
status: pending
keywords_matched: {', '.join(message['keywords'])}
---

# WhatsApp Message

**From:** {sender}  
**Received:** {datetime.fromisoformat(message['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}  
**Keywords:** {', '.join(message['keywords'])}

---

## Message Content

{message_content}

---

# Suggested Actions
- [ ] Review message
- [ ] Reply to sender
- [ ] Take required action
- [ ] Mark as read in WhatsApp
- [ ] Archive after processing

---
*Generated by WhatsApp Watcher v0.1 (Silver Tier)*

**Note:** Verify message in WhatsApp before responding. Session: {self.session_path.name}
'''
        filepath = self.needs_action / filename
        filepath.write_text(content)
        
        self.logger.info(f"Created action file: {filename}")
        return filepath
    
    def _sanitize_field(self, text: str) -> str:
        """Sanitize text for YAML frontmatter."""
        return text.replace('"', '').replace('\n', ' ').strip()[:100]
    
    def run(self):
        """Main loop - continuously check for new messages."""
        self.logger.info('=' * 50)
        self.logger.info('WhatsApp Watcher starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Session: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Keywords: {self.keywords}')
        self.logger.info('=' * 50)
        
        # Check if session exists
        if not any(self.session_path.iterdir()):
            self.logger.warning("No session data found.")
            self.logger.warning("First run: Open browser manually to scan QR code.")
            self.logger.warning("Session will be saved for future runs.")
        
        super().run()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='WhatsApp Watcher - Monitor WhatsApp Web for messages'
    )
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--session', '-s',
                       help='Path to session folder (default: ~/.whatsapp_session)')
    parser.add_argument('--interval', '-i', type=int, default=30,
                       help='Check interval in seconds (default: 30)')
    parser.add_argument('--keywords', '-k', nargs='+',
                       help='Keywords to filter messages')
    parser.add_argument('--quiet-start', type=int, default=22,
                       help='Quiet hours start hour (default: 22)')
    parser.add_argument('--quiet-end', type=int, default=6,
                       help='Quiet hours end hour (default: 6)')
    parser.add_argument('--config', '-c', help='Path to config JSON file')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Load config from file if provided
    config = {}
    if args.config:
        import json
        config_path = Path(args.config)
        if config_path.exists():
            config = json.loads(config_path.read_text())
    
    # Session path
    if args.session:
        session_path = Path(args.session)
    else:
        session_path = config.get('session_path', Path.home() / '.whatsapp_session')
    
    # Keywords
    keywords = args.keywords or config.get('keywords', ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing'])
    
    # Quiet hours
    quiet_hours = {
        'start': args.quiet_start or config.get('quiet_hours', {}).get('start', 22),
        'end': args.quiet_end or config.get('quiet_hours', {}).get('end', 6)
    }
    
    # Check if playwright is installed
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: Playwright not installed")
        print("Install with: pip install playwright")
        print("Then run: playwright install chromium")
        sys.exit(1)
    
    # Create watcher
    watcher = WhatsAppWatcher(
        str(vault_path),
        str(session_path),
        keywords=keywords,
        check_interval=args.interval or config.get('check_interval', 30),
        quiet_hours=quiet_hours
    )
    
    watcher.run()


if __name__ == '__main__':
    main()
