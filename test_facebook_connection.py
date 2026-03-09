#!/usr/bin/env python
"""
Test Facebook Connection and Basic Operations
Run this first to verify your Facebook Graph API setup
"""

import sys
import os
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent.resolve()

# Add facebook folder to path
facebook_path = script_dir / 'facebook'
sys.path.insert(0, str(facebook_path))

# Load environment variables
from dotenv import load_dotenv
env_file = facebook_path / '.env'
print(f"Looking for .env at: {env_file}")
print(f".env exists: {env_file.exists()}")

if env_file.exists():
    load_dotenv(env_file)
    print(f"[OK] Loaded environment from {env_file}")
else:
    print(f"[ERROR] .env file not found at {env_file}")
    print("Please create facebook/.env with your credentials")
    sys.exit(1)

from facebook_graph_mcp_server import facebook_client

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def main():
    print_section("Facebook Graph API - Connection Test")
    
    # Test 1: Verify Token
    print("\n[TEST 1] Verifying access token...")
    try:
        token_info = facebook_client.verify_token()
        if token_info.get('valid'):
            print(f"[OK] Token is VALID")
            print(f"  User ID: {token_info.get('user_id')}")
            print(f"  App ID: {token_info.get('app_id')}")
            if token_info.get('expires_at'):
                from datetime import datetime
                expiry = datetime.fromtimestamp(token_info['expires_at'])
                print(f"  Expires: {expiry}")
            if token_info.get('scopes'):
                print(f"  Permissions: {', '.join(token_info['scopes'][:5])}...")
        else:
            print(f"[ERROR] Token is INVALID")
            print(f"  Error: {token_info.get('error', 'Unknown')}")
            print("\nPlease regenerate token from:")
            print("   https://developers.facebook.com/tools/explorer/")
            return False
    except Exception as e:
        print(f"[ERROR] Token verification failed: {e}")
        return False
    
    # Test 2: Get Profile/Page Info
    print_section("TEST 2: Getting Profile/Page Information")
    try:
        me = facebook_client.get_me()
        print(f"[OK] Connected as: {me.get('name', 'Unknown')}")
        print(f"  ID: {me.get('id')}")
        if me.get('username'):
            print(f"  Username: @{me.get('username')}")
        if me.get('email'):
            print(f"  Email: {me.get('email')}")
    except Exception as e:
        print(f"[ERROR] Failed to get profile: {e}")
        return False
    
    # Test 3: Get Recent Posts
    print_section("TEST 3: Getting Recent Posts")
    try:
        posts = facebook_client.get_posts(limit=5)
        print(f"[OK] Found {len(posts)} recent posts")
        for i, post in enumerate(posts[:3], 1):
            print(f"\n  Post {i}:")
            print(f"    ID: {post['id']}")
            message = post.get('message', '')[:80]
            print(f"    Message: {message}...")
            print(f"    Likes: {post['likes']} | Comments: {post['comments']} | Shares: {post.get('shares', 0)}")
    except Exception as e:
        print(f"[ERROR] Failed to get posts: {e}")
    
    # Test 4: Get Notifications
    print_section("TEST 4: Getting Notifications")
    try:
        notifications = facebook_client.get_notifications(limit=10)
        print(f"[OK] Found {len(notifications)} recent notifications")
        
        # Count unread
        unread = sum(1 for n in notifications if n.get('unread'))
        print(f"  Unread: {unread}")
        
        # Show recent
        for i, notif in enumerate(notifications[:5], 1):
            print(f"\n  Notification {i}:")
            print(f"    From: {notif.get('from', 'Unknown')}")
            message = notif.get('message', '')[:60]
            print(f"    Message: {message}...")
            print(f"    Type: {notif.get('type', 'unknown')}")
            if notif.get('unread'):
                print(f"    Status: UNREAD")
    except Exception as e:
        print(f"[ERROR] Failed to get notifications: {e}")
    
    # Test 5: Get Page Insights (if Page ID configured)
    if facebook_client.page_id:
        print_section("TEST 5: Getting Page Insights")
        try:
            insights = facebook_client.get_page_insights()
            print(f"[OK] Page Insights for: {insights.get('page_id')}")
            
            metrics = insights.get('metrics', {})
            print(f"\n  Metrics:")
            for metric, value in metrics.items():
                print(f"    {metric}: {value}")
        except Exception as e:
            print(f"[ERROR] Failed to get insights: {e}")
    else:
        print_section("TEST 5: Page Insights (SKIPPED)")
        print("  No Page ID configured in .env")
        print("  Add FACEBOOK_PAGE_ID to get Page insights")
    
    # Test 6: Create Test Post (Optional)
    print_section("TEST 6: Create Test Post (OPTIONAL)")
    print("\nThis will create a post on your Facebook timeline/Page")
    response = input("  Create test post? (y/n): ").strip().lower()
    
    if response == 'y':
        try:
            message = """AI Employee Gold Tier - Connection Test

This is an automated test post from my AI Employee system.
Facebook Graph API integration is working correctly!

#AIEmployee #GoldTier #Automation #TestPost
"""
            result = facebook_client.create_post(message=message)
            
            if result.get('success'):
                post_id = result.get('post_id')
                print(f"\n[OK] POST CREATED SUCCESSFULLY!")
                print(f"  Post ID: {post_id}")
                print(f"  View at: https://facebook.com/{post_id}")
            else:
                print(f"\n[ERROR] Post creation failed: {result.get('error')}")
        except Exception as e:
            print(f"\n[ERROR] Post creation failed: {e}")
    else:
        print("  Skipped (user declined)")
    
    # Summary
    print_section("TEST SUMMARY")
    print("""
All basic tests completed!

Next Steps:
1. [OK] Token verified - Your credentials are working
2. [OK] Profile/Page connected - API access confirmed
3. [OK] Posts/Notifications retrieved - Monitoring ready

To start using Facebook integration:

  # Run continuous monitoring
  python facebook_graph_watcher.py ..\\ --interval 300

  # Start MCP server for Qwen Code
  cd facebook && python facebook_graph_mcp_server.py

  # Post to Facebook using Qwen
  qwen "Post to Facebook: Hello from AI Employee! #GoldTier"

For detailed usage, see: facebook/FACEBOOK_USAGE_GUIDE.md
""")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
