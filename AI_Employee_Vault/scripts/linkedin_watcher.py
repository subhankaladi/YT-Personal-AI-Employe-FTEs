#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher/Poster - Monitor and post to LinkedIn.

WARNING: This uses LinkedIn automation which may violate LinkedIn's Terms of Service.
Use at your own risk and only for personal accounts.

Usage:
    python linkedin_watcher.py /path/to/vault --authenticate  # First time
    python linkedin_watcher.py /path/to/vault --post "Hello LinkedIn!"
    python linkedin_watcher.py /path/to/vault --check  # Check for notifications
"""

import sys
import time
import logging
import argparse
import json
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LinkedInWatcher:
    """Monitor and post to LinkedIn using browser automation."""
    
    def __init__(self, vault_path: str, session_path: str,
                 check_interval: int = 300, keywords: List[str] = None):
        """
        Initialize LinkedIn Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to save browser session
            check_interval: Seconds between checks (default: 300 = 5 min)
            keywords: Keywords to monitor in notifications
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)
        self.check_interval = check_interval
        self.keywords = keywords or ['comment', 'message', 'connection', 'job']
        
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        
        # Ensure directories exist
        self.needs_action.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.processed_notifications = set()
    
    def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn (save session).
        
        Returns:
            True if successful
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser for login
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/login')
                
                self.logger.info("Please log in to LinkedIn manually...")
                self.logger.info("Session will be saved for future use.")
                
                # Wait for user to log in (max 5 minutes)
                try:
                    page.wait_for_url('https://www.linkedin.com/feed/*', timeout=300000)
                    self.logger.info("Login detected!")
                    time.sleep(2)  # Let session fully load
                    browser.close()
                    return True
                except PlaywrightTimeout:
                    self.logger.warning("Login timeout. Try again.")
                    browser.close()
                    return False
                    
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def check_notifications(self) -> List[Dict]:
        """
        Check LinkedIn notifications.
        
        Returns:
            List of new notifications
        """
        notifications = []
        
        try:
            with sync_playwright() as p:
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
                
                # Navigate to notifications
                self.logger.debug("Navigating to LinkedIn notifications...")
                page.goto('https://www.linkedin.com/notifications/', wait_until='networkidle')
                
                # Wait for notifications list
                try:
                    page.wait_for_selector('[data-test-id="notification-list"]', timeout=15000)
                    self.logger.debug("Notifications loaded")
                except PlaywrightTimeout:
                    self.logger.warning("Notifications did not load. May need to re-authenticate.")
                    browser.close()
                    return []
                
                # Small delay for content to load
                time.sleep(2)
                
                # Find notification items
                try:
                    notification_items = page.query_selector_all('[data-test-id="notification-item"]')
                    self.logger.debug(f"Found {len(notification_items)} notifications")
                    
                    for item in notification_items[:10]:  # Limit to 10
                        try:
                            text = item.inner_text(timeout=2000)
                            notification_id = item.get_attribute('id') or str(hash(text))
                            
                            # Check if already processed
                            if notification_id not in self.processed_notifications:
                                # Check for keywords
                                text_lower = text.lower()
                                matched = [kw for kw in self.keywords if kw in text_lower]
                                
                                if matched:
                                    notifications.append({
                                        'id': notification_id,
                                        'text': text,
                                        'keywords': matched,
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    self.processed_notifications.add(notification_id)
                                    self.logger.info(f"Found notification with keywords: {matched}")
                        except Exception:
                            continue
                            
                except Exception as e:
                    self.logger.error(f"Error finding notifications: {e}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error checking notifications: {e}")
        
        return notifications
    
    def post_update(self, content: str, hashtags: List[str] = None,
                    screenshot: bool = True) -> Dict:
        """
        Post update to LinkedIn.
        
        Args:
            content: Post content
            hashtags: List of hashtags (without #)
            screenshot: Take screenshot after posting
            
        Returns:
            Dict with post result
        """
        result = {'status': 'unknown', 'content': content}
        
        try:
            with sync_playwright() as p:
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
                
                # Navigate to feed
                self.logger.debug("Navigating to LinkedIn feed...")
                page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
                
                # Wait for post creation box
                try:
                    page.wait_for_selector('[aria-label="Start a post"]', timeout=30000)
                    self.logger.debug("Feed loaded")
                except PlaywrightTimeout:
                    self.logger.error("Feed did not load. May need to re-authenticate.")
                    browser.close()
                    result['status'] = 'auth_error'
                    return result
                
                # Small delay to appear human
                time.sleep(2)
                
                # Click "Start a post"
                self.logger.debug("Clicking 'Start a post'...")
                page.click('[aria-label="Start a post"]')
                
                # Wait for post dialog
                page.wait_for_selector('.ql-editor', timeout=10000)
                time.sleep(1)
                
                # Prepare content with hashtags
                full_content = content
                if hashtags:
                    hashtag_str = ' '.join([f'#{tag}' for tag in hashtags])
                    full_content = f"{content}\n\n{hashtag_str}"
                
                # Type content
                self.logger.debug("Typing content...")
                page.fill('.ql-editor', full_content)
                
                # Human-like delay
                time.sleep(2)
                
                # Click "Post" button
                self.logger.debug("Clicking 'Post'...")
                post_button = page.locator('button:has-text("Post")').first
                post_button.click()
                
                # Wait for success toast
                try:
                    page.wait_for_selector('.post-updated-toast, .toast', timeout=10000)
                    self.logger.info("Post successful!")
                    result['status'] = 'posted'
                    result['timestamp'] = datetime.now().isoformat()
                except PlaywrightTimeout:
                    self.logger.warning("Post confirmation not detected")
                    result['status'] = 'uncertain'
                
                # Take screenshot
                if screenshot and result['status'] == 'posted':
                    screenshot_path = self.done / f'linkedin_{int(time.time())}.png'
                    page.screenshot(path=str(screenshot_path))
                    result['screenshot'] = str(screenshot_path)
                    self.logger.info(f"Screenshot saved: {screenshot_path.name}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error posting: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def create_notification_action_file(self, notification: Dict) -> Path:
        """Create action file for important notification."""
        timestamp = datetime.now().isoformat()
        filename = f'LINKEDIN_NOTIF_{int(time.time())}.md'
        
        content = f'''---
type: linkedin_notification
received: {timestamp}
keywords: {', '.join(notification['keywords'])}
status: pending
---

# LinkedIn Notification

## Content

{notification['text']}

## Keywords Matched

{', '.join(notification['keywords'])}

## Suggested Actions

- [ ] Review notification
- [ ] Respond if needed (comment/message)
- [ ] Check LinkedIn for context
- [ ] Archive after processing

---
*Generated by LinkedIn Watcher v0.1 (Silver Tier)*
'''
        filepath = self.needs_action / filename
        filepath.write_text(content)
        
        self.logger.info(f"Created notification action file: {filename}")
        return filepath
    
    def run(self):
        """Main loop - continuously check for notifications."""
        self.logger.info('=' * 50)
        self.logger.info('LinkedIn Watcher starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Session: {self.session_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info(f'Keywords: {self.keywords}')
        self.logger.info('=' * 50)
        
        # Check if session exists
        if not any(self.session_path.iterdir()):
            self.logger.warning("No session data found.")
            self.logger.warning("Run with --authenticate first to log in.")
            return
        
        self.logger.info("Starting notification monitoring...")
        
        while True:
            try:
                notifications = self.check_notifications()
                
                for notif in notifications:
                    self.create_notification_action_file(notif)
                
            except Exception as e:
                self.logger.error(f"Error in check loop: {e}")
            
            time.sleep(self.check_interval)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Watcher/Poster')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--session', '-s', help='Path to session folder')
    parser.add_argument('--interval', '-i', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--keywords', '-k', nargs='+',
                       help='Keywords to monitor')
    parser.add_argument('--authenticate', '-a', action='store_true',
                       help='Run authentication flow')
    parser.add_argument('--post', '-p', help='Post content to LinkedIn')
    parser.add_argument('--hashtags', '-H', nargs='+', default=['business', 'tech'],
                       help='Hashtags for post (default: business tech)')
    parser.add_argument('--check', '-c', action='store_true',
                       help='Check notifications once')
    parser.add_argument('--config', help='Path to config JSON file')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Load config
    config = {}
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config = json.loads(config_path.read_text())
    
    # Session path
    session_path = Path(args.session) if args.session else config.get('session_path', vault_path / '.linkedin_session')
    
    # Create watcher
    watcher = LinkedInWatcher(
        str(vault_path),
        str(session_path),
        args.interval or config.get('check_interval', 300),
        args.keywords or config.get('keywords', ['comment', 'message', 'connection', 'job'])
    )
    
    if args.authenticate:
        print("Starting LinkedIn authentication...")
        print("A browser window will open. Log in to LinkedIn.")
        print("Session will be saved for future use.")
        print()
        if watcher.authenticate():
            print("")
            print("Authentication successful!")
            print("You can now post or check notifications.")
        else:
            print("")
            print("Authentication failed")
            sys.exit(1)
    
    elif args.post:
        print(f"Posting to LinkedIn: {args.post[:50]}...")
        result = watcher.post_update(args.post, args.hashtags)
        print(f"Result: {result['status']}")
        if result.get('screenshot'):
            print(f"Screenshot: {result['screenshot']}")
    
    elif args.check:
        print("Checking notifications...")
        notifications = watcher.check_notifications()
        if notifications:
            print(f"Found {len(notifications)} new notifications:")
            for n in notifications:
                print(f"  - {n['keywords']}: {n['text'][:50]}...")
        else:
            print("No new notifications.")
    
    else:
        # Run continuous watcher
        watcher.run()


if __name__ == '__main__':
    main()
