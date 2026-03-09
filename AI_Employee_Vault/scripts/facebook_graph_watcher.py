# Facebook Graph API Watcher - Gold Tier
# Monitors Facebook using official Graph API for notifications and messages

import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict
from base_watcher import BaseWatcher
import requests

logger = logging.getLogger("facebook_graph_watcher")

# Facebook Graph API Configuration
FACEBOOK_ACCESS_TOKEN = ""  # Set via environment or config
FACEBOOK_PAGE_ID = ""  # Set via environment or config
FACEBOOK_API_VERSION = "v19.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"

class FacebookGraphWatcher(BaseWatcher):
    """Monitor Facebook using Graph API for notifications and messages"""
    
    def __init__(
        self, 
        vault_path: str, 
        access_token: str = None,
        page_id: str = None,
        check_interval: int = 300
    ):
        super().__init__(vault_path, check_interval)
        self.access_token = access_token or FACEBOOK_ACCESS_TOKEN
        self.page_id = page_id or FACEBOOK_PAGE_ID
        self.session = requests.Session()
        self.keywords = ["urgent", "asap", "invoice", "payment", "help", "pricing", "quote"]
        self.processed_ids = set()
        self.last_check_time = datetime.now() - timedelta(minutes=5)
        
        if not self.access_token:
            logger.warning("Facebook access token not configured")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make request to Facebook Graph API"""
        url = f"{FACEBOOK_GRAPH_URL}/{endpoint}"
        
        request_params = {
            "access_token": self.access_token
        }
        if params:
            request_params.update(params)
        
        try:
            response = self.session.get(url, params=request_params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                logger.error(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")
                return {}
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {}
    
    def verify_token(self) -> bool:
        """Verify the access token is valid"""
        result = self._make_request("me", {"fields": "id,name"})
        return "id" in result
    
    def check_for_updates(self) -> List[Dict]:
        """Check for new notifications and messages"""
        items = []
        
        if not self.access_token:
            logger.warning("Facebook access token not configured, skipping check")
            return items
        
        # Check notifications
        notifications = self.get_notifications()
        for notif in notifications:
            if notif["id"] not in self.processed_ids:
                # Check if notification contains important keywords
                message_lower = notif.get("message", "").lower()
                is_important = any(kw in message_lower for kw in self.keywords)
                
                if is_important or notif.get("unread", False):
                    items.append({
                        "type": "notification",
                        "id": notif["id"],
                        "from": notif.get("from", "Unknown"),
                        "message": notif.get("message", ""),
                        "created_time": notif.get("created_time"),
                        "priority": "high" if is_important else "normal"
                    })
                self.processed_ids.add(notif["id"])
        
        # Check messages (if Page ID configured)
        if self.page_id:
            messages = self.get_messages()
            for msg in messages:
                if msg["id"] not in self.processed_ids:
                    message_lower = msg.get("message", "").lower()
                    is_important = any(kw in message_lower for kw in self.keywords)
                    
                    if is_important:
                        items.append({
                            "type": "message",
                            "id": msg["id"],
                            "from": msg.get("from", "Unknown"),
                            "message": msg.get("message", ""),
                            "created_time": msg.get("created_time"),
                            "priority": "high" if is_important else "normal"
                        })
                    self.processed_ids.add(msg["id"])
        
        self.last_check_time = datetime.now()
        return items
    
    def get_notifications(self, limit: int = 20) -> List[Dict]:
        """Get recent notifications"""
        result = self._make_request(
            "me/notifications",
            {
                "limit": limit,
                "fields": "id,from,message,created_time,unread,type"
            }
        )
        
        notifications = []
        for item in result.get("data", []):
            # Only get recent notifications
            created_time = item.get("created_time")
            if created_time:
                try:
                    notif_time = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                    if notif_time > self.last_check_time:
                        notifications.append(item)
                except:
                    notifications.append(item)
            else:
                notifications.append(item)
        
        return notifications[:limit]
    
    def get_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages from Page inbox"""
        if not self.page_id:
            return []
        
        result = self._make_request(
            f"{self.page_id}/conversations",
            {
                "limit": limit,
                "fields": "id,updated_time,messages{from,message,created_time}",
                "platform": "facebook"
            }
        )
        
        messages = []
        for conv in result.get("data", []):
            for msg in conv.get("messages", {}).get("data", [])[:5]:
                # Only get recent messages
                created_time = msg.get("created_time")
                if created_time:
                    try:
                        msg_time = datetime.fromisoformat(created_time.replace("Z", "+00:00"))
                        if msg_time > self.last_check_time:
                            messages.append(msg)
                    except:
                        messages.append(msg)
                else:
                    messages.append(msg)
        
        return messages[:limit]
    
    def create_action_file(self, item: Dict) -> Path:
        """Create action file in Needs_Action folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        item_type = item["type"]
        priority = item.get("priority", "normal")
        
        filename = f"FACEBOOK_{item_type.upper()}_{timestamp}_{item['id'][:8]}.md"
        filepath = self.needs_action / filename
        
        content = f"""---
type: facebook_{item_type}
source: Facebook Graph API
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
item_id: {item['id']}
from: {item.get('from', 'Unknown')}
created_time: {item.get('created_time', 'Unknown')}
---

# Facebook {item_type.title()} Alert

## Details
- **Type**: {item_type}
- **From**: {item.get('from', 'Unknown')}
- **Priority**: {priority}
- **Received**: {item.get('created_time', 'Unknown')}

## Message
{item.get('message', 'No content')}

## Suggested Actions
- [ ] Review the notification/message
- [ ] Respond if necessary using Facebook MCP
- [ ] Create follow-up task
- [ ] Archive after processing

## Quick Reply Commands
```bash
# Reply via Facebook MCP
python -m facebook_graph_mcp_server --comment "{item['id']}" --message "Thank you for your message. We'll get back to you shortly."

# Create post response
python -m facebook_graph_mcp_server --post "Response to {item.get('from', 'customer')}: [Your response]"
```

---
*Generated by Facebook Graph API Watcher - Gold Tier*
"""
        
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Created action file: {filepath}")
        return filepath
    
    def post_to_facebook(self, message: str, link: str = None, photo_url: str = None) -> Dict:
        """Post to Facebook using Graph API"""
        endpoint = f"{self.page_id}/feed" if self.page_id else "me/feed"
        
        data = {
            "message": message,
            "access_token": self.access_token
        }
        
        if link:
            data["link"] = link
        if photo_url:
            data["picture"] = photo_url
        
        try:
            url = f"{FACEBOOK_GRAPH_URL}/{endpoint}"
            response = self.session.post(url, data=data, timeout=30)
            result = response.json()
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"].get("message", "Unknown error")
                }
            
            return {
                "success": True,
                "post_id": result.get("id"),
                "message": "Post created successfully"
            }
            
        except Exception as e:
            logger.error(f"Post error: {e}")
            return {"success": False, "error": str(e)}
    
    def run_test(self) -> bool:
        """Run a test check"""
        print("Testing Facebook Graph API Watcher...")
        print("=" * 50)
        
        # Verify token
        print("1. Verifying access token...")
        if not self.verify_token():
            print("   ✗ Token verification failed")
            return False
        print("   ✓ Token is valid")
        
        # Check notifications
        print("2. Checking notifications...")
        notifications = self.get_notifications(5)
        print(f"   Found {len(notifications)} recent notifications")
        for notif in notifications[:3]:
            print(f"     - {notif.get('from', {}).get('name', 'Unknown')}: {notif.get('message', '')[:50]}...")
        
        # Check messages
        if self.page_id:
            print("3. Checking messages...")
            messages = self.get_messages(5)
            print(f"   Found {len(messages)} recent messages")
            for msg in messages[:3]:
                print(f"     - {msg.get('from', {}).get('name', 'Unknown')}: {msg.get('message', '')[:50]}...")
        
        print("=" * 50)
        print("✓ Test completed successfully")
        return True


def main():
    """Main entry point"""
    import argparse
    from dotenv import load_dotenv
    import os
    
    parser = argparse.ArgumentParser(description="Facebook Graph API Watcher - Gold Tier")
    parser.add_argument("vault_path", type=str, help="Path to Obsidian vault")
    parser.add_argument("--access-token", type=str, help="Facebook access token")
    parser.add_argument("--page-id", type=str, help="Facebook Page ID")
    parser.add_argument("--interval", type=int, default=300, help="Check interval in seconds")
    parser.add_argument("--test", action="store_true", help="Run single test check")
    parser.add_argument("--verify", action="store_true", help="Verify token only")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--config", type=str, help="Path to config file (.env)")
    
    args = parser.parse_args()
    
    # Load config from .env file if specified
    if args.config:
        load_dotenv(args.config)
        access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        page_id = os.getenv("FACEBOOK_PAGE_ID")
    else:
        access_token = args.access_token or FACEBOOK_ACCESS_TOKEN
        page_id = args.page_id or FACEBOOK_PAGE_ID
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create watcher
    watcher = FacebookGraphWatcher(
        vault_path=args.vault_path,
        access_token=access_token,
        page_id=page_id,
        check_interval=args.interval
    )
    
    if args.verify:
        # Just verify token
        if watcher.verify_token():
            print("✓ Facebook access token is valid")
            return 0
        else:
            print("✗ Facebook access token is invalid")
            return 1
    
    elif args.test:
        # Run test
        success = watcher.run_test()
        return 0 if success else 1
    
    else:
        # Run continuous monitoring
        print(f"Starting Facebook Graph API Watcher (interval: {args.interval}s)")
        print(f"Vault: {args.vault_path}")
        print(f"Page ID: {page_id or 'User Profile'}")
        print("Press Ctrl+C to stop")
        
        # Verify token before starting
        if not watcher.verify_token():
            print("✗ Facebook access token is invalid!")
            print("Please set FACEBOOK_ACCESS_TOKEN in your environment or use --access-token flag")
            return 1
        
        print("✓ Access token verified")
        
        try:
            watcher.run()
        except KeyboardInterrupt:
            print("\nStopping Facebook Graph API Watcher...")
            return 0


if __name__ == "__main__":
    import sys
    sys.exit(main() or 0)
