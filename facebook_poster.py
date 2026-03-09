#!/usr/bin/env python
"""
Interactive Facebook Poster
Easy script to post to Facebook and check comments
"""

import sys
from pathlib import Path

# Add facebook folder to path
facebook_path = Path(__file__).parent.parent / 'facebook'
sys.path.insert(0, str(facebook_path))

# Load environment
from dotenv import load_dotenv
env_file = facebook_path / '.env'
if env_file.exists():
    load_dotenv(env_file)
else:
    print(f"✗ .env file not found at {env_file}")
    sys.exit(1)

from facebook_graph_mcp_server import facebook_client

def print_menu():
    print("\n" + "=" * 50)
    print("  Facebook Auto-Poster - Gold Tier")
    print("=" * 50)
    print("\n  1. Post to Facebook (Text)")
    print("  2. Post to Facebook (with Link)")
    print("  3. Post Photo")
    print("  4. View Recent Posts")
    print("  5. View Comments on Post")
    print("  6. View Notifications")
    print("  7. View Page Insights")
    print("  8. Quick Test Post")
    print("  0. Exit")
    print()

def create_post():
    """Create a text post"""
    print("\n--- Create Text Post ---")
    message = input("\nEnter your post message:\n> ")
    
    if len(message) < 5:
        print("✗ Message too short!")
        return
    
    # Add hashtags if not present
    if not message.strip().endswith('#'):
        message += "\n\n#AIEmployee #GoldTier #Automation"
    
    confirm = input(f"\nPost this? (y/n): {message[:100]}... ").strip().lower()
    if confirm == 'y':
        try:
            result = facebook_client.create_post(message=message)
            if result.get('success'):
                print(f"\n✓ POSTED SUCCESSFULLY!")
                print(f"  Post ID: {result.get('post_id')}")
                print(f"  View: https://facebook.com/{result.get('post_id')}")
            else:
                print(f"\n✗ Post failed: {result.get('error')}")
        except Exception as e:
            print(f"\n✗ Error: {e}")

def create_post_with_link():
    """Create a post with link"""
    print("\n--- Create Post with Link ---")
    message = input("Enter your post message:\n> ")
    link = input("Enter link URL:\n> ")
    
    confirm = input(f"\nPost this? (y/n): {message[:50]}... + {link} ").strip().lower()
    if confirm == 'y':
        try:
            result = facebook_client.create_post(message=message, link=link)
            if result.get('success'):
                print(f"\n✓ POSTED SUCCESSFULLY!")
                print(f"  Post ID: {result.get('post_id')}")
            else:
                print(f"\n✗ Post failed: {result.get('error')}")
        except Exception as e:
            print(f"\n✗ Error: {e}")

def create_photo_post():
    """Create a photo post"""
    print("\n--- Create Photo Post ---")
    message = input("Enter photo caption:\n> ")
    photo_url = input("Enter photo URL (must be public):\n> ")
    
    confirm = input(f"\nPost this photo? (y/n): {photo_url} ").strip().lower()
    if confirm == 'y':
        try:
            result = facebook_client.create_photo_post(message=message, photo_url=photo_url)
            if result.get('success'):
                print(f"\n✓ PHOTO POSTED SUCCESSFULLY!")
                print(f"  Post ID: {result.get('post_id')}")
            else:
                print(f"\n✗ Post failed: {result.get('error')}")
        except Exception as e:
            print(f"\n✗ Error: {e}")

def view_recent_posts():
    """View recent posts"""
    print("\n--- Recent Posts ---")
    try:
        posts = facebook_client.get_posts(limit=10)
        if not posts:
            print("No posts found")
            return
        
        for i, post in enumerate(posts, 1):
            print(f"\n{i}. Post ID: {post['id']}")
            message = post.get('message', '')[:100]
            print(f"   Message: {message}...")
            print(f"   👍 {post['likes']} | 💬 {post['comments']} | 🔄 {post.get('shares', 0)}")
            print(f"   Time: {post['created_time']}")
    except Exception as e:
        print(f"✗ Error: {e}")

def view_comments():
    """View comments on a post"""
    print("\n--- View Comments ---")
    post_id = input("Enter Post ID: ").strip()
    
    if not post_id:
        print("✗ No Post ID provided")
        return
    
    try:
        comments = facebook_client.get_comments(post_id, limit=20)
        if not comments:
            print("No comments found")
            return
        
        print(f"\nFound {len(comments)} comments:\n")
        for i, comment in enumerate(comments, 1):
            print(f"{i}. {comment['from']}")
            print(f"   {comment['message']}")
            print(f"   👍 {comment.get('like_count', 0)} | {comment['created_time']}")
            print()
    except Exception as e:
        print(f"✗ Error: {e}")

def view_notifications():
    """View notifications"""
    print("\n--- Recent Notifications ---")
    try:
        notifications = facebook_client.get_notifications(limit=15)
        if not notifications:
            print("No notifications found")
            return
        
        unread_count = sum(1 for n in notifications if n.get('unread'))
        print(f"Total: {len(notifications)} | Unread: {unread_count}\n")
        
        for i, notif in enumerate(notifications, 1):
            icon = "🔴" if notif.get('unread') else "⚪"
            print(f"{icon} {i}. {notif.get('from', 'Unknown')}")
            print(f"   {notif.get('message', '')[:80]}")
            print(f"   Type: {notif.get('type', 'unknown')} | Time: {notif.get('created_time', '')}")
            print()
    except Exception as e:
        print(f"✗ Error: {e}")

def view_insights():
    """View page insights"""
    print("\n--- Page Insights ---")
    
    if not facebook_client.page_id:
        print("✗ No Page ID configured in .env")
        return
    
    try:
        insights = facebook_client.get_page_insights()
        print(f"Page: {insights.get('page_id')}")
        print(f"Time: {insights.get('timestamp')}")
        
        metrics = insights.get('metrics', {})
        print("\nMetrics:")
        for metric, value in metrics.items():
            print(f"  {metric}: {value}")
    except Exception as e:
        print(f"✗ Error: {e}")

def quick_test_post():
    """Create a quick test post"""
    print("\n--- Quick Test Post ---")
    message = """
🤖 AI Employee Gold Tier Test

Testing my automated AI Employee system!
Facebook Graph API integration is working perfectly.

#AIEmployee #GoldTier #Automation #TestPost
"""
    confirm = input("Post test message? (y/n): ").strip().lower()
    if confirm == 'y':
        try:
            result = facebook_client.create_post(message=message)
            if result.get('success'):
                print(f"\n✓ TEST POSTED!")
                print(f"  Post ID: {result.get('post_id')}")
                print(f"  View: https://facebook.com/{result.get('post_id')}")
            else:
                print(f"\n✗ Post failed: {result.get('error')}")
        except Exception as e:
            print(f"\n✗ Error: {e}")

def main():
    print("\n✓ Facebook Auto-Poster Loaded!")
    print(f"  Connected to: {facebook_client.page_id or 'User Profile'}")
    
    while True:
        print_menu()
        choice = input("Select option: ").strip()
        
        if choice == '1':
            create_post()
        elif choice == '2':
            create_post_with_link()
        elif choice == '3':
            create_photo_post()
        elif choice == '4':
            view_recent_posts()
        elif choice == '5':
            view_comments()
        elif choice == '6':
            view_notifications()
        elif choice == '7':
            view_insights()
        elif choice == '8':
            quick_test_post()
        elif choice == '0':
            print("\nGoodbye! 👋")
            break
        else:
            print("✗ Invalid option")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted! Goodbye.")
        sys.exit(0)
