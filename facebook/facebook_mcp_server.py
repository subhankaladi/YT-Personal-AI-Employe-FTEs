# Facebook Integration - Gold Tier
# Facebook Watcher and MCP Server for posting and monitoring

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("facebook-mcp-server")

# Facebook Configuration
FACEBOOK_EMAIL = os.getenv("FACEBOOK_EMAIL", "")
FACEBOOK_PASSWORD = os.getenv("FACEBOOK_PASSWORD", "")
FACEBOOK_SESSION_PATH = os.getenv("FACEBOOK_SESSION_PATH", 
    str(Path.home() / ".facebook_session"))

class FacebookClient:
    """Client for Facebook automation via Playwright"""
    
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
    def start_browser(self):
        """Start browser with persistent context"""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        
        self.browser = self.playwright.chromium.launch_persistent_context(
            self.session_path,
            headless=True,
            user_data_dir=self.session_path,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )
        
        if not self.browser.pages:
            self.page = self.browser.new_page()
        else:
            self.page = self.browser.pages[0]
        
        # Hide automation flags
        self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
    def stop_browser(self):
        """Stop browser"""
        if self.browser:
            self.browser.close()
            self.browser = None
        if self.playwright:
            self.playwright.stop()
            self.playwright = None
            
    def is_logged_in(self) -> bool:
        """Check if already logged in"""
        try:
            if not self.page:
                return False
            
            # Check for Facebook home page elements
            self.page.goto("https://www.facebook.com", timeout=10000)
            self.page.wait_for_load_state("networkidle", timeout=15000)
            
            # Look for logged-in indicators
            menu_button = self.page.query_selector('[aria-label="Menu"]')
            messenger_button = self.page.query_selector('[aria-label="Messenger"]')
            
            return menu_button is not None or messenger_button is not None
            
        except Exception as e:
            logger.debug(f"Login check error: {e}")
            return False
    
    def login(self, email: str, password: str) -> bool:
        """Login to Facebook"""
        try:
            self.start_browser()
            
            if self.is_logged_in():
                logger.info("Already logged in")
                return True
            
            # Navigate to Facebook
            self.page.goto("https://www.facebook.com", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Find and fill email
            email_field = self.page.locator('input[type="email"]').first
            email_field.fill(email)
            
            # Find and fill password
            password_field = self.page.locator('input[type="password"]').first
            password_field.fill(password)
            
            # Click login button
            login_button = self.page.locator('button[type="submit"]').first
            login_button.click()
            
            # Wait for navigation
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Check if login successful
            return self.is_logged_in()
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False
    
    def create_post(self, content: str, privacy: str = "public") -> Dict:
        """Create a Facebook post"""
        try:
            if not self.page:
                self.start_browser()
            
            if not self.is_logged_in():
                return {"success": False, "error": "Not logged in"}
            
            # Navigate to home page
            self.page.goto("https://www.facebook.com", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Find the "What's on your mind?" input
            # Facebook frequently changes selectors, so we try multiple approaches
            post_input = None
            
            # Try different selectors
            selectors = [
                'div[role="textbox"][aria-label="What\'s on your mind?"]',
                'div[role="textbox"][aria-label="What\'s on your mind?, {name}"]',
                'input[aria-label="What\'s on your mind?"]',
                'div[data-testid="create_post"]',
                '[placeholder="What\'s on your mind?"]'
            ]
            
            for selector in selectors:
                try:
                    post_input = self.page.locator(selector).first
                    if post_input.count() > 0:
                        break
                except:
                    continue
            
            if not post_input or post_input.count() == 0:
                # Try alternative: click the create post area first
                create_post_btn = self.page.locator('text="What\'s on your mind?"').first
                if create_post_btn.count() > 0:
                    create_post_btn.click()
                    self.page.wait_for_timeout(2000)
                    post_input = self.page.locator('div[role="textbox"]').first
            
            if not post_input or post_input.count() == 0:
                return {"success": False, "error": "Could not find post input field"}
            
            # Fill post content
            post_input.fill(content)
            self.page.wait_for_timeout(1000)
            
            # Set privacy if needed
            if privacy == "friends":
                try:
                    privacy_btn = self.page.locator('[aria-label*="Privacy"]').first
                    privacy_btn.click()
                    self.page.wait_for_timeout(1000)
                    friends_option = self.page.locator('text="Friends"').first
                    friends_option.click()
                except:
                    logger.warning("Could not set privacy setting")
            
            # Find and click post button
            post_selectors = [
                'button:has-text("Post")',
                '[aria-label="Post"]',
                'div[role="button"]:has-text("Post")'
            ]
            
            post_button = None
            for selector in post_selectors:
                try:
                    post_button = self.page.locator(selector).first
                    if post_button.count() > 0 and post_button.is_enabled():
                        break
                except:
                    continue
            
            if post_button and post_button.is_enabled():
                post_button.click()
                self.page.wait_for_timeout(3000)
                
                return {
                    "success": True,
                    "message": "Post created successfully",
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"success": False, "error": "Post button not found or disabled"}
                
        except Exception as e:
            logger.error(f"Create post error: {e}")
            return {"success": False, "error": str(e)}
    
    def get_notifications(self, limit: int = 10) -> List[Dict]:
        """Get recent Facebook notifications"""
        try:
            if not self.page:
                self.start_browser()
            
            if not self.is_logged_in():
                return []
            
            # Navigate to notifications
            self.page.goto("https://www.facebook.com/notifications", timeout=30000)
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            notifications = []
            
            # Find notification items
            notification_items = self.page.locator('[role="article"]').all()[:limit]
            
            for item in notification_items:
                try:
                    text = item.inner_text()
                    time_elem = item.locator('[data-visualcompletion="css-img"]').first
                    
                    notifications.append({
                        "text": text,
                        "time": time_elem.inner_text() if time_elem.count() > 0 else "Unknown",
                        "timestamp": datetime.now().isoformat()
                    })
                except:
                    continue
            
            return notifications
            
        except Exception as e:
            logger.error(f"Get notifications error: {e}")
            return []
    
    def get_page_insights(self, page_name: str = None) -> Dict:
        """Get Facebook Page insights/analytics"""
        try:
            if not self.page:
                self.start_browser()
            
            if not self.is_logged_in():
                return {"error": "Not logged in"}
            
            # Navigate to professional dashboard or page
            if page_name:
                self.page.goto(f"https://www.facebook.com/{page_name}/insights", timeout=30000)
            else:
                self.page.goto("https://www.facebook.com/pages/?category=insights", timeout=30000)
            
            self.page.wait_for_load_state("networkidle", timeout=30000)
            
            # Extract insights data (simplified)
            insights = {
                "page_name": page_name or "Your Page",
                "timestamp": datetime.now().isoformat(),
                "message": "Navigate to your Facebook Page Insights for detailed analytics"
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Get insights error: {e}")
            return {"error": str(e)}

# Initialize Facebook client
facebook_client = FacebookClient(FACEBOOK_SESSION_PATH)

# Create MCP server
server = Server("facebook-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Facebook tools"""
    return [
        Tool(
            name="facebook_login",
            description="Login to Facebook (saves session for future use)",
            inputSchema={
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "Facebook email"},
                    "password": {"type": "string", "description": "Facebook password"}
                },
                "required": ["email", "password"]
            }
        ),
        Tool(
            name="facebook_create_post",
            description="Create a new Facebook post",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Post content"},
                    "privacy": {
                        "type": "string",
                        "description": "Privacy setting",
                        "enum": ["public", "friends"],
                        "default": "public"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="facebook_get_notifications",
            description="Get recent Facebook notifications",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of notifications", "default": 10}
                }
            }
        ),
        Tool(
            name="facebook_get_page_insights",
            description="Get Facebook Page insights/analytics",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_name": {"type": "string", "description": "Facebook Page name/ID"}
                }
            }
        ),
        Tool(
            name="facebook_check_session",
            description="Check if Facebook session is valid",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute Facebook tool"""
    try:
        if name == "facebook_login":
            email = arguments.get("email", FACEBOOK_EMAIL)
            password = arguments.get("password", FACEBOOK_PASSWORD)
            
            if not email or not password:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Email and password required"}, indent=2)
                )]
            
            success = facebook_client.login(email, password)
            
            if success:
                facebook_client.stop_browser()
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "message": "Logged in successfully. Session saved."
                    }, indent=2)
                )]
            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": "Login failed"}, indent=2)
                )]
        
        elif name == "facebook_create_post":
            content = arguments["content"]
            privacy = arguments.get("privacy", "public")
            
            result = facebook_client.create_post(content, privacy)
            
            # Clean up browser after posting
            facebook_client.stop_browser()
            
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "facebook_get_notifications":
            limit = arguments.get("limit", 10)
            notifications = facebook_client.get_notifications(limit)
            
            facebook_client.stop_browser()
            
            return [TextContent(
                type="text",
                text=json.dumps({"notifications": notifications}, indent=2)
            )]
        
        elif name == "facebook_get_page_insights":
            page_name = arguments.get("page_name")
            insights = facebook_client.get_page_insights(page_name)
            
            facebook_client.stop_browser()
            
            return [TextContent(
                type="text",
                text=json.dumps(insights, indent=2)
            )]
        
        elif name == "facebook_check_session":
            is_logged_in = facebook_client.is_logged_in()
            
            if is_logged_in:
                facebook_client.stop_browser()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "logged_in": is_logged_in,
                    "session_path": str(facebook_client.session_path)
                }, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
            
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)}, indent=2)
        )]

async def main():
    """Run the Facebook MCP server"""
    logger.info("Starting Facebook MCP Server...")
    logger.info(f"Session path: {FACEBOOK_SESSION_PATH}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
