#!/usr/bin/env python
"""
Simple Facebook Comment Monitor
Checks for new comments on your posts
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
import requests
import os

# Load environment
script_dir = Path(__file__).parent.resolve()
facebook_path = script_dir / 'facebook'

from dotenv import load_dotenv
load_dotenv(facebook_path / '.env')

access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')
api_version = os.getenv('FACEBOOK_API_VERSION', 'v19.0')

# Keywords to detect important comments
KEYWORDS = ['urgent', 'asap', 'price', 'invoice', 'help', 'question', 'quote']

# Folders
vault_path = script_dir / 'AI_Employee_Vault'
needs_action = vault_path / 'Needs_Action'
logs_path = vault_path / 'Logs'

needs_action.mkdir(parents=True, exist_ok=True)
logs_path.mkdir(parents=True, exist_ok=True)

# Track processed comments
processed = set()
last_check = datetime.now()

print("=" * 60)
print("  Facebook Comment Monitor - Gold Tier")
print("=" * 60)
print(f"\nMonitoring Page: {page_id}")
print(f"Check interval: 60 seconds")
print(f"Keywords: {', '.join(KEYWORDS)}")
print(f"Action folder: {needs_action}")
print("\nPress Ctrl+C to stop\n")

def get_posts():
    """Get recent posts"""
    url = f"https://graph.facebook.com/{api_version}/{page_id}/feed"
    params = {'access_token': access_token, 'limit': 5}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json().get('data', [])
    except:
        return []

def get_comments(post_id):
    """Get comments on a post"""
    url = f"https://graph.facebook.com/{api_version}/{post_id}/comments"
    params = {'access_token': access_token, 'limit': 50}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json().get('data', [])
    except:
        return []

def create_action_file(post, comment):
    """Create action file for important comment"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"FACEBOOK_COMMENT_{timestamp}_{comment['id'][:8]}.md"
    filepath = needs_action / filename
    
    content = f"""---
type: facebook_comment
post_id: {post['id']}
comment_id: {comment['id']}
from: {comment['from']['name']}
received: {datetime.now().isoformat()}
priority: high
---

# Facebook Comment Needs Response

**From:** {comment['from']['name']}
**Post:** {post.get('message', '')[:100]}
**Comment:** {comment['message']}

## Action
- [ ] Draft response
- [ ] Post reply using Facebook MCP
- [ ] Archive when done
"""
    
    filepath.write_text(content, encoding='utf-8')
    return filepath

check_count = 0

try:
    while True:
        check_count += 1
        check_time = datetime.now()
        
        print(f"[{check_time.strftime('%H:%M:%S')}] Check #{check_count}...")
        
        # Get posts
        posts = get_posts()
        print(f"  Found {len(posts)} posts")
        
        for post in posts:
            post_id = post['id']
            comments = get_comments(post_id)
            
            for comment in comments:
                if comment['id'] in processed:
                    continue
                
                processed.add(comment['id'])
                
                # Check if recent
                try:
                    comment_time = datetime.fromisoformat(
                        comment['created_time'].replace('Z', '+00:00')
                    ).replace(tzinfo=None)
                    
                    if comment_time <= last_check:
                        continue
                except:
                    pass
                
                # Check for keywords
                message = comment.get('message', '').lower()
                is_important = any(kw in message for kw in KEYWORDS)
                
                print(f"  New comment from {comment['from'].get('name', 'Unknown')}")
                
                if is_important:
                    print(f"    [IMPORTANT] Contains keyword")
                    action_file = create_action_file(post, comment)
                    print(f"    Created: {action_file.name}")
                    
                    # Log
                    log_file = logs_path / f"facebook_{datetime.now().strftime('%Y%m%d')}.jsonl"
                    with open(log_file, 'a') as f:
                        f.write(json.dumps({
                            'timestamp': datetime.now().isoformat(),
                            'type': 'important_comment',
                            'from': comment['from']['name'],
                            'message': comment['message']
                        }) + '\n')
                else:
                    print(f"    [OK] No action needed")
        
        last_check = check_time
        time.sleep(60)  # Check every 60 seconds
        
except KeyboardInterrupt:
    print(f"\n\nStopped by user")
    print(f"Total checks: {check_count}")
    print(f"Comments tracked: {len(processed)}")
