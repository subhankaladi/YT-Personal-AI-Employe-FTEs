# Facebook Watcher - Gold Tier
# Monitors Facebook for notifications, messages, and mentions

import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from base_watcher import BaseWatcher
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

logger = logging.getLogger("facebook_watcher")

class FacebookWatcher(BaseWatcher):
    """Monitor Facebook for notifications and messages"""
    
    def __init__(self, vault_path: str, session_path: str = None, check_interval: int = 300):
        super().__init__(vault_path, check_interval)
        self.session_path = Path(session_path) if session_path else Path.home() / ".facebook_session"
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.keywords = ["urgent", "asap", "invoice", "payment", "help", "pricing", "quote"]
        self.processed_ids = set()
        self.playwright = None
        self.browser = None
        self.page = None
        
    def start_browser(self):
        """Start browser with persistent context"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch_persistent_context(
            str(self.session_path),
            headless=True,
            user_data_dir=str(self.session_path),
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        if not self.browser.pages:
            self.page = self.browser.new_page()
        else:
            self.page = self.browser.pages[0]
    
    def stop_browser(self):
        """Stop browser"""
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
    
    def is_logged_in(self) -> bool:
        """Check if logged in to Facebook"""
        try:
            if not self.page:
                self.start_browser()
            
            self.page.goto("https://www.facebook.com", timeout=15000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
            
            # Check for logged-in indicators
            menu_button = self.page.query_selector('[aria-label="Menu"]')
            return menu_button is not None
            
        except Exception as e:
            logger.debug(f"Login check error: {e}")
            return False
    
    def login(self, email: str, password: str) -> bool:
        """Login to Facebook"""
        try:
            self.start_browser()
            
            if self.is_logged_in():
                return True
            
            self.page.goto("https://www.facebook.com", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Fill credentials
            email_field = self.page.locator('input[type="email"]').first
            email_field.fill(email)
            
            password_field = self.page.locator('input[type="password"]').first
            password_field.fill(password)
            
            # Click login
            login_button = self.page.locator('button[type="submit"]').first
            login_button.click()
            
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            return self.is_logged_in()
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def check_for_updates(self) -> List[Dict]:
        """Check for new Facebook notifications and messages"""
        items = []
        
        try:
            if not self.page:
                self.start_browser()
            
            if not self.is_logged_in():
                logger.warning("Not logged in to Facebook")
                self.stop_browser()
                return items
            
            # Check notifications
            notifications = self.get_notifications()
            for notif in notifications:
                if notif["id"] not in self.processed_ids:
                    # Check if notification contains important keywords
                    text_lower = notif["text"].lower()
                    if any(kw in text_lower for kw in self.keywords):
                        items.append({
                            "type": "notification",
                            "id": notif["id"],
                            "text": notif["text"],
                            "time": notif["time"],
                            "priority": "high" if any(kw in text_lower for kw in ["urgent", "asap"]) else "normal"
                        })
                    self.processed_ids.add(notif["id"])
            
            # Check messages (if Messenger accessible)
            messages = self.get_messages()
            for msg in messages:
                if msg["id"] not in self.processed_ids:
                    text_lower = msg["text"].lower()
                    if any(kw in text_lower for kw in self.keywords):
                        items.append({
                            "type": "message",
                            "id": msg["id"],
                            "from": msg["from"],
                            "text": msg["text"],
                            "time": msg["time"],
                            "priority": "high" if any(kw in text_lower for kw in ["urgent", "asap"]) else "normal"
                        })
                    self.processed_ids.add(msg["id"])
            
            self.stop_browser()
            
        except Exception as e:
            logger.error(f"Error checking Facebook: {e}")
            self.stop_browser()
        
        return items
    
    def get_notifications(self) -> List[Dict]:
        """Get recent notifications"""
        try:
            self.page.goto("https://www.facebook.com/notifications", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            notifications = []
            notification_items = self.page.locator('[role="article"]').all()[:20]
            
            for i, item in enumerate(notification_items):
                try:
                    text = item.inner_text()
                    time_elem = item.locator('[data-visualcompletion="css-img"]').first
                    
                    notifications.append({
                        "id": f"notif_{int(time.time())}_{i}",
                        "text": text,
                        "time": time_elem.inner_text() if time_elem.count() > 0 else "Unknown"
                    })
                except:
                    continue
            
            return notifications
            
        except Exception as e:
            logger.error(f"Get notifications error: {e}")
            return []
    
    def get_messages(self) -> List[Dict]:
        """Get recent Messenger messages"""
        try:
            # Try to access Messenger
            self.page.goto("https://www.messenger.com", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            messages = []
            
            # Find message previews
            message_items = self.page.locator('[role="row"]').all()[:10]
            
            for i, item in enumerate(message_items):
                try:
                    text = item.inner_text()
                    
                    # Check for unread indicator
                    is_unread = item.locator('[aria-label*="unread"]').count() > 0
                    
                    if is_unread:
                        messages.append({
                            "id": f"msg_{int(time.time())}_{i}",
                            "from": "Facebook Messenger",
                            "text": text,
                            "time": datetime.now().strftime("%H:%M")
                        })
                except:
                    continue
            
            return messages
            
        except Exception as e:
            logger.debug(f"Get messages error: {e}")
            return []
    
    def create_action_file(self, item: Dict) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        item_type = item["type"]
        priority = item.get("priority", "normal")
        
        filename = f"FACEBOOK_{item_type.upper()}_{timestamp}_{item['id'][:8]}.md"
        filepath = self.needs_action / filename
        
        content = f"""---
type: facebook_{item_type}
source: Facebook
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
item_id: {item['id']}
---

# Facebook {item_type.title()} Alert

## Details
- **Type**: {item_type}
- **Priority**: {priority}
- **Received**: {item.get('time', 'Unknown')}

## Content
{item.get('text', 'No content')}

## Suggested Actions
- [ ] Review the notification/message
- [ ] Respond if necessary
- [ ] Create follow-up task
- [ ] Archive after processing

---
*Generated by Facebook Watcher - Gold Tier*
"""
        
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Created action file: {filepath}")
        return filepath
    
    def run_interactive_login(self):
        """Run interactive login to save session"""
        print("Facebook Interactive Login")
        print("=" * 40)
        print("This will open a browser to login to Facebook.")
        print("The session will be saved for future use.")
        print()
        
        email = input("Enter Facebook email: ").strip()
        password = input("Enter Facebook password: ").strip()
        
        print("\nLogging in...")
        success = self.login(email, password)
        
        if success:
            print("✓ Login successful! Session saved.")
            print(f"Session path: {self.session_path}")
        else:
            print("✗ Login failed. Please try again.")
        
        self.stop_browser()
        return success
    
    def cleanup(self):
        """Clean up resources"""
        self.stop_browser()

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Facebook Watcher - Gold Tier")
    parser.add_argument("vault_path", type=str, help="Path to Obsidian vault")
    parser.add_argument("--session-path", type=str, help="Path to save session")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds")
    parser.add_argument("--login", action="store_true", help="Run interactive login")
    parser.add_argument("--test", action="store_true", help="Run single test check")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create watcher
    watcher = FacebookWatcher(
        vault_path=args.vault_path,
        session_path=args.session_path,
        check_interval=args.interval
    )
    
    if args.login:
        watcher.run_interactive_login()
    elif args.test:
        print("Testing Facebook Watcher...")
        items = watcher.check_for_updates()
        print(f"Found {len(items)} items:")
        for item in items:
            print(f"  - [{item['priority']}] {item['type']}: {item['text'][:50]}...")
        watcher.cleanup()
    else:
        # Run continuous monitoring
        print(f"Starting Facebook Watcher (interval: {args.interval}s)")
        print(f"Vault: {args.vault_path}")
        print(f"Session: {watcher.session_path}")
        print("Press Ctrl+C to stop")
        
        try:
            watcher.run()
        except KeyboardInterrupt:
            print("\nStopping Facebook Watcher...")
            watcher.cleanup()

if __name__ == "__main__":
    main()
