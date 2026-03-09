#!/usr/bin/env python
"""
Facebook Token Generator Guide
Shows you exactly how to get a token with the right permissions
"""

print("=" * 70)
print("  HOW TO GET A FACEBOOK TOKEN WITH CORRECT PERMISSIONS")
print("=" * 70)

print("""
STEP 1: Go to Facebook Graph API Explorer
------------------------------------------------
URL: https://developers.facebook.com/tools/explorer/


STEP 2: Select YOUR App
------------------------------------------------
- Click the dropdown at the top of the page
- Select your app: "AI Employee" (App ID: 2337703573417748)


STEP 3: Get User Access Token
------------------------------------------------
- Click "Get Token" button (top right)
- Select "Get User Access Token"
- A popup window will appear


STEP 4: Select Required Permissions
------------------------------------------------
In the popup, check these boxes:

  [YES] pages_manage_posts        - To post to your Page
  [YES] pages_read_engagement     - To read insights/comments
  [YES] pages_read_user_content   - To read comments/messages
  [YES] pages_messaging           - To send/receive messages
  [YES] user_notifications        - To get notifications
  [YES] publish_to_groups         - For group posting (optional)

Click "Continue"


STEP 5: Generate Token
------------------------------------------------
- Facebook will ask you to log in
- Click "Continue as [Your Name]"
- Review permissions and click "OK"
- The token will appear in the "Access Token" field
- Click the copy icon to copy it


STEP 6: Update Your .env File
------------------------------------------------
Open: facebook\\.env

Replace the FACEBOOK_ACCESS_TOKEN line with your NEW token


STEP 7: Test the Token
------------------------------------------------
Run: python test_facebook_post.py

You should see: [SUCCESS] POST CREATED!
""")

print("=" * 70)
print("  TROUBLESHOOTING")
print("=" * 70)

print("""
Problem: "App_id mismatch" error
Solution: Make sure YOUR app is selected in the dropdown at Step 2

Problem: "Permission denied" error  
Solution: Make sure you checked ALL the permission boxes in Step 4

Problem: Can't find pages_manage_posts permission
Solution: Your app may need to be submitted for review
         For testing, you can still post as an admin

Problem: Token expires quickly
Solution: Get a long-lived token (valid for 60 days):
         https://developers.facebook.com/docs/facebook-login/access-tokens/
""")

print("=" * 70)
print("  QUICK LINKS")
print("=" * 70)
print("""
Graph API Explorer:     https://developers.facebook.com/tools/explorer/
Your App Dashboard:     https://developers.facebook.com/apps/2337703573417748/
Access Token Guide:     https://developers.facebook.com/docs/facebook-login/access-tokens/
Permission Reference:   https://developers.facebook.com/docs/permissions/
""")

print("=" * 70)
