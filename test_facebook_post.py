#!/usr/bin/env python
"""
Simple Facebook Post Test
Creates a test post on your Facebook Page
"""

import sys
from pathlib import Path
import requests
import os

# Get script directory
script_dir = Path(__file__).parent.resolve()
facebook_path = script_dir / 'facebook'

# Load environment
from dotenv import load_dotenv
load_dotenv(facebook_path / '.env')

# Get credentials
access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')
api_version = os.getenv('FACEBOOK_API_VERSION', 'v19.0')

print("=" * 60)
print("  Facebook Post Test")
print("=" * 60)

print(f"\nPage ID: {page_id}")
print(f"API Version: {api_version}")

# Create post message
message = """AI Employee Gold Tier - Test Post

Testing my automated AI Employee system with Facebook Graph API integration!

Features:
- Odoo ERP Integration
- Facebook Auto-Posting
- Comment Monitoring
- CEO Briefing Generator

#AIEmployee #GoldTier #Automation #FacebookAPI
"""

print(f"\nPosting message...")
print(f"Message length: {len(message)} characters")

# Post to Facebook Page
url = f"https://graph.facebook.com/{api_version}/{page_id}/feed"
params = {
    'message': message,
    'access_token': access_token
}

try:
    response = requests.post(url, params=params, timeout=30)
    result = response.json()
    
    print(f"\nResponse status: {response.status_code}")
    
    if 'error' in result:
        print(f"\n[ERROR] Post failed:")
        print(f"  Message: {result['error'].get('message', 'Unknown')}")
        print(f"  Type: {result['error'].get('type', 'Unknown')}")
        
        # Check for common errors
        error_msg = result['error'].get('message', '')
        if 'permission' in error_msg.lower():
            print("\n[HELP] Permission error - make sure you granted:")
            print("  - pages_manage_posts")
            print("  - pages_read_engagement")
        elif 'token' in error_msg.lower():
            print("\n[HELP] Token error - regenerate your access token")
    else:
        post_id = result.get('id')
        print(f"\n[SUCCESS] POST CREATED!")
        print(f"  Post ID: {post_id}")
        print(f"  View at: https://facebook.com/{post_id}")
        
except requests.exceptions.RequestException as e:
    print(f"\n[ERROR] Request failed: {e}")
except Exception as e:
    print(f"\n[ERROR] Unexpected error: {e}")

print("\n" + "=" * 60)
