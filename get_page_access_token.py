#!/usr/bin/env python
"""
Get Page Access Token for Posting
This script shows you how to get a Page Access Token with posting permissions
"""

import sys
from pathlib import Path
import requests
import os

# Load environment
script_dir = Path(__file__).parent.resolve()
facebook_path = script_dir / 'facebook'

from dotenv import load_dotenv
load_dotenv(facebook_path / '.env')

user_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')

print("=" * 70)
print("  GET PAGE ACCESS TOKEN FOR POSTING")
print("=" * 70)

print(f"""
Current User Token: {user_token[:30]}...
Page ID: {page_id}

To post to your Page, you need a PAGE ACCESS TOKEN, not just a user token.

HERE'S HOW TO GET IT:
""")

print("=" * 70)
print("  METHOD 1: Using Graph API Explorer (EASIEST)")
print("=" * 70)

print("""
1. Go to: https://developers.facebook.com/tools/explorer/

2. Select your app: AI Employee (2337703573417748)

3. Click "Get Token" -> "Get Page Access Token"

4. Select your page: "FTE Personal AI Employee"

5. Check these permissions:
   [YES] pages_manage_posts
   [YES] pages_read_engagement
   [YES] pages_read_user_content
   [YES] pages_messaging
   [YES] content_management

6. Click "Generate Access Token"

7. Facebook will ask you to choose a Page
   Select: FTE Personal AI Employee

8. Copy the Page Access Token

9. Update facebook\\.env:
   FACEBOOK_ACCESS_TOKEN=NEW_PAGE_TOKEN_HERE
""")

print("=" * 70)
print("  METHOD 2: Exchange User Token for Page Token")
print("=" * 70)

# Try to get page token using user token
print("\nTrying to get Page Access Token automatically...\n")

url = f"https://graph.facebook.com/v19.0/{page_id}"
params = {
    'fields': 'access_token',
    'access_token': user_token
}

try:
    response = requests.get(url, params=params, timeout=10)
    result = response.json()
    
    if 'access_token' in result:
        page_token = result['access_token']
        print(f"[OK] Got Page Access Token!")
        print(f"\nPage Token: {page_token}")
        print(f"\n[INFO] Update your facebook\\.env with this token:")
        print(f"FACEBOOK_ACCESS_TOKEN={page_token}")
        
        # Test the page token
        print("\n" + "=" * 70)
        print("  TESTING PAGE TOKEN")
        print("=" * 70)
        
        # Test posting with page token
        post_url = f"https://graph.facebook.com/v19.0/{page_id}/feed"
        post_params = {
            'message': 'Testing page token...',
            'access_token': page_token
        }
        
        post_response = requests.post(post_url, params=post_params, timeout=10)
        post_result = post_response.json()
        
        if 'id' in post_result:
            print(f"\n[SUCCESS] POST CREATED WITH PAGE TOKEN!")
            print(f"Post ID: {post_result['id']}")
            print(f"View: https://facebook.com/{post_result['id']}")
            print("\n[INFO] Save this page token in facebook\\.env")
        else:
            print(f"\n[ERROR] Post failed: {post_result.get('error', {}).get('message', 'Unknown')}")
            print("\n[INFO] Use Method 1 above to get Page token manually")
    else:
        print(f"[ERROR] Could not get Page Access Token")
        if 'error' in result:
            print(f"Error: {result['error'].get('message', 'Unknown')}")
        print("\n[INFO] Use Method 1 above to get Page token manually")
        
except Exception as e:
    print(f"[ERROR] {e}")
    print("\n[INFO] Use Method 1 above to get Page token manually")

print("\n" + "=" * 70)
print("  IMPORTANT NOTES")
print("=" * 70)
print("""
- A Page Access Token is DIFFERENT from a User Access Token
- Page tokens don't expire (unless you change your password)
- You must be an ADMIN of the Page to get posting permissions
- Make sure your app has "pages_manage_posts" permission approved

After updating the token in facebook\\.env, run:
  python test_facebook_post.py
""")

print("=" * 70)
