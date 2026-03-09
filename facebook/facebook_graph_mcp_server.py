# Facebook Graph API MCP Server - Gold Tier
# Official Facebook API integration for posting and monitoring

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("facebook-graph-mcp-server")

# Facebook Graph API Configuration
FACEBOOK_APP_ID = os.getenv("FACEBOOK_APP_ID", "")
FACEBOOK_APP_SECRET = os.getenv("FACEBOOK_APP_SECRET", "")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "")
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_API_VERSION = "v19.0"
FACEBOOK_GRAPH_URL = f"https://graph.facebook.com/{FACEBOOK_API_VERSION}"

class FacebookGraphClient:
    """Client for Facebook Graph API"""
    
    def __init__(self, access_token: str, page_id: str = None):
        self.access_token = access_token
        self.page_id = page_id
        self.session = requests.Session()
        self.base_url = FACEBOOK_GRAPH_URL
        
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Make request to Facebook Graph API"""
        url = f"{self.base_url}/{endpoint}"
        
        params = {
            "access_token": self.access_token
        }
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method == "POST":
                response = self.session.post(url, params=params, json=data, timeout=30)
            elif method == "DELETE":
                response = self.session.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            result = response.json()
            
            # Check for API errors
            if "error" in result:
                raise Exception(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            raise Exception(f"Facebook API request failed: {str(e)}")
    
    def get_me(self) -> Dict:
        """Get current user or page info"""
        fields = "id,name,email"
        if self.page_id:
            endpoint = self.page_id
            fields += ",username,about,website,followers_count"
        else:
            endpoint = "me"
        
        return self._make_request(f"{endpoint}?fields={fields}")
    
    def create_post(self, message: str, link: str = None, photo_url: str = None, 
                    privacy: str = "EVERYONE") -> Dict:
        """Create a post on Facebook"""
        endpoint = f"{self.page_id}/feed" if self.page_id else "me/feed"
        
        data = {
            "message": message,
            "privacy": json.dumps({"value": privacy})
        }
        
        if link:
            data["link"] = link
        if photo_url:
            data["picture"] = photo_url
        
        result = self._make_request(endpoint, method="POST", data=data)
        
        return {
            "success": True,
            "post_id": result.get("id"),
            "message": "Post created successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    def create_photo_post(self, message: str, photo_url: str) -> Dict:
        """Create a photo post on Facebook"""
        endpoint = f"{self.page_id}/photos" if self.page_id else "me/photos"
        
        data = {
            "message": message,
            "url": photo_url
        }
        
        result = self._make_request(endpoint, method="POST", data=data)
        
        return {
            "success": True,
            "post_id": result.get("id"),
            "message": "Photo post created successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_posts(self, limit: int = 10) -> List[Dict]:
        """Get recent posts from page or profile"""
        endpoint = f"{self.page_id}/feed" if self.page_id else "me/posts"
        
        params = {
            "access_token": self.access_token,
            "limit": limit,
            "fields": "id,message,created_time,updated_time,likes.summary(true),comments.summary(true),shares"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")
        
        posts = []
        for item in result.get("data", []):
            posts.append({
                "id": item.get("id"),
                "message": item.get("message", ""),
                "created_time": item.get("created_time"),
                "updated_time": item.get("updated_time"),
                "likes": item.get("likes", {}).get("summary", {}).get("total_count", 0),
                "comments": item.get("comments", {}).get("summary", {}).get("total_count", 0),
                "shares": item.get("shares", {}).get("count", 0)
            })
        
        return posts
    
    def get_notifications(self, limit: int = 10) -> List[Dict]:
        """Get recent notifications"""
        endpoint = "me/notifications"
        
        params = {
            "access_token": self.access_token,
            "limit": limit,
            "fields": "id,from,message,created_time,unread,type"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")
        
        notifications = []
        for item in result.get("data", []):
            notifications.append({
                "id": item.get("id"),
                "from": item.get("from", {}).get("name", "Unknown"),
                "message": item.get("message", ""),
                "created_time": item.get("created_time"),
                "unread": item.get("unread", False),
                "type": item.get("type", "")
            })
        
        return notifications
    
    def get_page_insights(self, metrics: List[str] = None) -> Dict:
        """Get Facebook Page insights/analytics"""
        if not self.page_id:
            return {"error": "Page ID required for insights"}
        
        if metrics is None:
            metrics = [
                "page_impressions_unique",
                "page_reach",
                "page_post_engagements",
                "page_likes",
                "page_follows",
                "page_views_total"
            ]
        
        endpoint = f"{self.page_id}/insights"
        
        params = {
            "access_token": self.access_token,
            "metric": ",".join(metrics),
            "period": "day"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")
        
        insights = {
            "page_id": self.page_id,
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        for item in result.get("data", []):
            metric_name = item.get("name")
            values = item.get("values", [])
            if values:
                insights["metrics"][metric_name] = values[-1].get("value", 0)
        
        return insights
    
    def get_comments(self, post_id: str, limit: int = 10) -> List[Dict]:
        """Get comments on a post"""
        endpoint = f"{post_id}/comments"
        
        params = {
            "access_token": self.access_token,
            "limit": limit,
            "fields": "id,from,message,created_time,like_count"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        result = response.json()
        
        if "error" in result:
            raise Exception(f"Facebook API error: {result['error'].get('message', 'Unknown error')}")
        
        comments = []
        for item in result.get("data", []):
            comments.append({
                "id": item.get("id"),
                "from": item.get("from", {}).get("name", "Unknown"),
                "message": item.get("message", ""),
                "created_time": item.get("created_time"),
                "like_count": item.get("like_count", 0)
            })
        
        return comments
    
    def create_comment(self, post_id: str, message: str) -> Dict:
        """Create a comment on a post"""
        endpoint = f"{post_id}/comments"
        
        data = {
            "message": message
        }
        
        result = self._make_request(endpoint, method="POST", data=data)
        
        return {
            "success": True,
            "comment_id": result.get("id"),
            "message": "Comment created successfully",
            "timestamp": datetime.now().isoformat()
        }
    
    def get_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages from Page inbox (requires Page access)"""
        if not self.page_id:
            return []
        
        endpoint = f"{self.page_id}/conversations"
        
        params = {
            "access_token": self.access_token,
            "limit": limit,
            "fields": "id,updated_time,messages{from,message,created_time}",
            "platform": "facebook"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        result = response.json()
        
        if "error" in result:
            logger.warning(f"Could not retrieve messages: {result['error'].get('message', 'Unknown error')}")
            return []
        
        messages = []
        for conv in result.get("data", []):
            for msg in conv.get("messages", {}).get("data", [])[:5]:
                messages.append({
                    "id": msg.get("id"),
                    "from": msg.get("from", {}).get("name", "Unknown"),
                    "message": msg.get("message", ""),
                    "created_time": msg.get("created_time"),
                    "conversation_id": conv.get("id")
                })
        
        return messages[:limit]
    
    def verify_token(self) -> Dict:
        """Verify the access token is valid"""
        endpoint = "debug_token"
        
        params = {
            "input_token": self.access_token,
            "access_token": f"{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}"
        }
        
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=30)
        result = response.json()
        
        if "error" in result:
            return {
                "valid": False,
                "error": result["error"].get("message", "Invalid token")
            }
        
        data = result.get("data", {})
        return {
            "valid": data.get("is_valid", False),
            "user_id": data.get("user_id"),
            "app_id": data.get("app_id"),
            "expires_at": data.get("expires_at"),
            "scopes": data.get("scopes", [])
        }

# Initialize Facebook client
facebook_client = FacebookGraphClient(
    access_token=FACEBOOK_ACCESS_TOKEN,
    page_id=FACEBOOK_PAGE_ID
)

# Create MCP server
server = Server("facebook-graph-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Facebook Graph API tools"""
    return [
        Tool(
            name="facebook_verify_token",
            description="Verify Facebook access token is valid",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="facebook_get_me",
            description="Get current user or page information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="facebook_create_post",
            description="Create a new Facebook post (requires pages_manage_posts permission)",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Post content"},
                    "link": {"type": "string", "description": "Optional link to share"},
                    "photo_url": {"type": "string", "description": "Optional photo URL"},
                    "privacy": {
                        "type": "string",
                        "description": "Privacy setting",
                        "enum": ["EVERYONE", "ALL_FRIENDS", "FRIENDS_OF_FRIENDS", "SELF"],
                        "default": "EVERYONE"
                    }
                },
                "required": ["message"]
            }
        ),
        Tool(
            name="facebook_create_photo_post",
            description="Create a photo post on Facebook",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "Photo caption"},
                    "photo_url": {"type": "string", "description": "URL of the photo"}
                },
                "required": ["message", "photo_url"]
            }
        ),
        Tool(
            name="facebook_get_posts",
            description="Get recent posts from page or profile",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of posts to retrieve", "default": 10}
                }
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
            description="Get Facebook Page insights/analytics (requires pages_read_engagement)",
            inputSchema={
                "type": "object",
                "properties": {
                    "metrics": {
                        "type": "array",
                        "description": "Metrics to retrieve",
                        "items": {"type": "string"},
                        "default": ["page_impressions_unique", "page_reach", "page_post_engagements"]
                    }
                }
            }
        ),
        Tool(
            name="facebook_get_comments",
            description="Get comments on a specific post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {"type": "string", "description": "Facebook post ID"},
                    "limit": {"type": "integer", "description": "Number of comments", "default": 10}
                },
                "required": ["post_id"]
            }
        ),
        Tool(
            name="facebook_create_comment",
            description="Create a comment on a post",
            inputSchema={
                "type": "object",
                "properties": {
                    "post_id": {"type": "string", "description": "Facebook post ID"},
                    "message": {"type": "string", "description": "Comment content"}
                },
                "required": ["post_id", "message"]
            }
        ),
        Tool(
            name="facebook_get_messages",
            description="Get recent messages from Page inbox (requires pages_messaging)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of messages", "default": 10}
                }
            }
        ),
        Tool(
            name="facebook_generate_hashtags",
            description="Generate relevant hashtags for a post",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Post topic or content"},
                    "count": {"type": "integer", "description": "Number of hashtags", "default": 5}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute Facebook Graph API tool"""
    try:
        if name == "facebook_verify_token":
            result = facebook_client.verify_token()
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "facebook_get_me":
            result = facebook_client.get_me()
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "facebook_create_post":
            result = facebook_client.create_post(
                message=arguments["message"],
                link=arguments.get("link"),
                photo_url=arguments.get("photo_url"),
                privacy=arguments.get("privacy", "EVERYONE")
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "facebook_create_photo_post":
            result = facebook_client.create_photo_post(
                message=arguments["message"],
                photo_url=arguments["photo_url"]
            )
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "facebook_get_posts":
            limit = arguments.get("limit", 10)
            posts = facebook_client.get_posts(limit)
            return [TextContent(
                type="text",
                text=json.dumps({"posts": posts}, indent=2)
            )]
        
        elif name == "facebook_get_notifications":
            limit = arguments.get("limit", 10)
            notifications = facebook_client.get_notifications(limit)
            
            # Filter for important keywords
            keywords = ["urgent", "asap", "invoice", "payment", "help", "pricing", "quote"]
            important = []
            for notif in notifications:
                if any(kw in notif.get("message", "").lower() for kw in keywords):
                    important.append(notif)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "notifications": notifications,
                    "important_count": len(important),
                    "total_count": len(notifications)
                }, indent=2)
            )]
        
        elif name == "facebook_get_page_insights":
            metrics = arguments.get("metrics")
            insights = facebook_client.get_page_insights(metrics)
            return [TextContent(
                type="text",
                text=json.dumps(insights, indent=2)
            )]
        
        elif name == "facebook_get_comments":
            post_id = arguments["post_id"]
            limit = arguments.get("limit", 10)
            comments = facebook_client.get_comments(post_id, limit)
            return [TextContent(
                type="text",
                text=json.dumps({"comments": comments}, indent=2)
            )]
        
        elif name == "facebook_create_comment":
            post_id = arguments["post_id"]
            message = arguments["message"]
            result = facebook_client.create_comment(post_id, message)
            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        
        elif name == "facebook_get_messages":
            limit = arguments.get("limit", 10)
            messages = facebook_client.get_messages(limit)
            
            # Filter for important keywords
            keywords = ["urgent", "asap", "invoice", "payment", "help", "pricing", "quote"]
            important = []
            for msg in messages:
                if any(kw in msg.get("message", "").lower() for kw in keywords):
                    important.append(msg)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "messages": messages,
                    "important_count": len(important),
                    "total_count": len(messages)
                }, indent=2)
            )]
        
        elif name == "facebook_generate_hashtags":
            topic = arguments.get("topic", "")
            count = arguments.get("count", 5)
            
            # Simple hashtag generation based on topic keywords
            base_hashtags = [
                "#business", "#marketing", "#socialmedia", "#digital", "#online",
                "#entrepreneur", "#success", "#growth", "#strategy", "#branding"
            ]
            
            # Generate topic-specific hashtags
            topic_words = topic.lower().split()
            topic_hashtags = [f"#{word}" for word in topic_words[:5]]
            
            all_hashtags = topic_hashtags + base_hashtags
            selected = all_hashtags[:count]
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "hashtags": selected,
                    "topic": topic,
                    "count": len(selected)
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
    """Run the Facebook Graph API MCP server"""
    logger.info("Starting Facebook Graph API MCP Server...")
    logger.info(f"API Version: {FACEBOOK_API_VERSION}")
    logger.info(f"Page ID: {FACEBOOK_PAGE_ID or 'User Profile'}")
    
    # Verify token on startup
    token_status = facebook_client.verify_token()
    if token_status.get("valid"):
        logger.info("Facebook access token is valid")
        logger.info(f"Token expires: {datetime.fromtimestamp(token_status.get('expires_at', 0)).isoformat()}")
    else:
        logger.warning(f"Facebook access token invalid: {token_status.get('error', 'Unknown error')}")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
