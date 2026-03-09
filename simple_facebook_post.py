#!/usr/bin/env python
"""
Simple Facebook Poster - Post to your Facebook Page
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

access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
page_id = os.getenv('FACEBOOK_PAGE_ID')
api_version = os.getenv('FACEBOOK_API_VERSION', 'v19.0')

print("=" * 60)
print("  Facebook Auto-Poster - Gold Tier")
print("=" * 60)
print(f"\nConnected to Page: {page_id}")
print()

# Get post content from command line or interactive
if len(sys.argv) > 1:
    message = ' '.join(sys.argv[1:])
else:
    print("Enter your post message (or 'quit' to exit):")
    print("-" * 60)
    lines = []
    while True:
        try:
            line = input()
            if line.lower() == 'quit':
                sys.exit(0)
            if line.strip() == '' and lines:
                break
            lines.append(line)
        except EOFError:
            break
    message = '\n'.join(lines)

if not message.strip():
    print("\n[ERROR] No message provided")
    sys.exit(1)

# Post to Facebook
print(f"\nPosting to Facebook...")
print(f"Message: {message[:100]}...")

url = f"https://graph.facebook.com/{api_version}/{page_id}/feed"
params = {
    'message': message,
    'access_token': access_token
}

try:
    response = requests.post(url, params=params, timeout=30)
    result = response.json()
    
    if 'id' in result:
        print(f"\n[SUCCESS] POST CREATED!")
        print(f"  Post ID: {result['id']}")
        print(f"  View at: https://facebook.com/{result['id']}")
    else:
        print(f"\n[ERROR] Post failed:")
        print(f"  {result.get('error', {}).get('message', 'Unknown error')}")
        
except Exception as e:
    print(f"\n[ERROR] {e}")

print("\n" + "=" * 60)
