# Facebook Graph API Setup Guide

Complete setup instructions for Facebook integration using the official Graph API.

## Overview

This integration uses the **official Facebook Graph API** instead of browser automation. This approach is:
- ✅ More reliable (no UI selector breaks)
- ✅ ToS compliant (official API)
- ✅ More secure (OAuth authentication)
- ✅ Feature-rich (insights, messages, posts)
- ✅ No account restriction risk

## Prerequisites

- Facebook Developer Account
- Facebook App (or create one during setup)
- Facebook Page (for business features)
- Python 3.13+

## Step 1: Create Facebook App

### 1.1 Go to Facebook Developers

1. Visit: https://developers.facebook.com/
2. Click **My Apps** → **Create App**
3. Select use case: **Other** → **Next**
4. Select app type: **Business** → **Next**
5. Fill in app details:
   - **App Name**: AI Employee FTE
   - **App Contact Email**: your-email@example.com
   - Click **Create App**

### 1.2 Configure App Settings

1. In app dashboard, go to **Settings** → **Basic**
2. Note down:
   - **App ID** (will be used later)
   - **App Secret** (click Show, copy it)
3. Add **Facebook Login** product:
   - Click **Add Product** → **Facebook Login**
   - Select **Web**
   - Set Site URL: `http://localhost:8069` (or your domain)
   - Set OAuth Redirect URI: `https://www.facebook.com/v19.0/dialog/oauth`

### 1.3 Configure App for Business Use

1. Go to **Settings** → **Basic**
2. Set **App Domain**: `localhost` (for testing) or your actual domain
3. Under **Business Verification**, complete verification if required
4. Enable **App in Development Mode** (for testing)

## Step 2: Get Access Token

### 2.1 Required Permissions

For full functionality, request these permissions:
- `pages_manage_posts` - Create posts on Page
- `pages_read_engagement` - Read Page insights
- `pages_read_user_content` - Read Page messages/comments
- `pages_messaging` - Send/receive messages
- `publish_to_groups` - Post to groups
- `user_posts` - Read user posts
- `user_notifications` - Read notifications

### 2.2 Generate Access Token (Graph API Explorer)

**For Testing/Development:**

1. Visit: https://developers.facebook.com/tools/explorer/
2. Select your app from dropdown
3. Click **Get Token** → **Get User Access Token**
4. Select permissions:
   - ✅ `pages_manage_posts`
   - ✅ `pages_read_engagement`
   - ✅ `pages_read_user_content`
   - ✅ `pages_messaging`
   - ✅ `user_posts`
   - ✅ `user_notifications`
5. Click **Generate Token**
6. Login to Facebook and approve permissions
7. Copy the generated **Access Token**

**For Production (Long-lived Token):**

1. Get short-lived token from Graph API Explorer (above)
2. Exchange for long-lived token:

```bash
curl -G "https://graph.facebook.com/v19.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=SHORT_LIVED_TOKEN"
```

This returns a token valid for ~60 days.

### 2.3 Get Page Access Token

For Page features (posts, insights, messages):

1. In Graph API Explorer, run:
```
/me/accounts
```

2. Find your page in results
3. Copy the `access_token` for your page
4. Note the page `id`

**Or use this query:**
```
/me/accounts?fields=id,name,access_token
```

## Step 3: Configure Environment

### 3.1 Create .env File

Create `facebook/.env` (do NOT commit to git):

```bash
# Facebook Graph API Configuration
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
FACEBOOK_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_page_id_here
FACEBOOK_API_VERSION=v19.0
```

### 3.2 Update System Environment (Optional)

For system-wide access, add to environment:

**Windows (PowerShell):**
```powershell
[Environment]::SetEnvironmentVariable("FACEBOOK_ACCESS_TOKEN", "your_token", "User")
[Environment]::SetEnvironmentVariable("FACEBOOK_PAGE_ID", "your_page_id", "User")
```

**Linux/Mac:**
```bash
export FACEBOOK_ACCESS_TOKEN="your_token"
export FACEBOOK_PAGE_ID="your_page_id"
```

## Step 4: Test Integration

### 4.1 Verify Token

```bash
cd AI_Employee_Vault\scripts

# Verify token is valid
python facebook_graph_watcher.py ..\ --verify
```

Expected output:
```
✓ Facebook access token is valid
```

### 4.2 Run Test Check

```bash
# Test notifications and messages
python facebook_graph_watcher.py ..\ --test
```

Expected output:
```
Testing Facebook Graph API Watcher...
==================================================
1. Verifying access token...
   ✓ Token is valid
2. Checking notifications...
   Found 5 recent notifications
     - John Doe: Commented on your post
     - Jane Smith: Mentioned you in a comment
3. Checking messages...
   Found 3 recent messages
     - Customer A: Hi, I need help with...
==================================================
✓ Test completed successfully
```

### 4.3 Test MCP Server

```bash
cd facebook

# Start MCP server
python facebook_graph_mcp_server.py

# In another terminal, test with Qwen Code
qwen "Check my Facebook notifications using the Facebook MCP"
```

## Step 5: Run Facebook Watcher

### Continuous Monitoring

```bash
cd AI_Employee_Vault\scripts

# Run watcher (checks every 5 minutes)
python facebook_graph_watcher.py ..\ --interval 300
```

### With Custom Config

```bash
python facebook_graph_watcher.py ..\ ^
  --access-token "your_token_here" ^
  --page-id "your_page_id_here" ^
  --interval 300
```

### With Config File

```bash
python facebook_graph_watcher.py ..\ ^
  --config facebook\.env ^
  --interval 300
```

## Step 6: Use Facebook MCP Tools

### Available Tools

| Tool | Description | Permission Required |
|------|-------------|---------------------|
| `facebook_verify_token` | Verify access token | None |
| `facebook_get_me` | Get user/page info | public_profile |
| `facebook_create_post` | Create text post | pages_manage_posts |
| `facebook_create_photo_post` | Create photo post | pages_manage_posts |
| `facebook_get_posts` | Get recent posts | pages_read_engagement |
| `facebook_get_notifications` | Get notifications | user_notifications |
| `facebook_get_page_insights` | Get analytics | pages_read_engagement |
| `facebook_get_comments` | Get post comments | pages_read_user_content |
| `facebook_create_comment` | Comment on post | pages_manage_posts |
| `facebook_get_messages` | Get Page messages | pages_messaging |
| `facebook_generate_hashtags` | Generate hashtags | None |

### Example Usage with Qwen Code

```bash
# Create a post
qwen "Post to Facebook: Excited to announce our new AI consulting service! #AI #Business"

# Get notifications
qwen "Check my Facebook notifications for any urgent messages"

# Get page insights
qwen "Get my Facebook page insights for the last 7 days"

# Reply to comments
qwen "Get comments on my latest post and draft responses"
```

### Example Usage with MCP Client

```bash
# Create post
python mcp-client.py call -u http://localhost:8810 \
  -t facebook_create_post \
  -p '{"message": "Hello from AI Employee Gold Tier!", "privacy": "EVERYONE"}'

# Get notifications
python mcp-client.py call -u http://localhost:8810 \
  -t facebook_get_notifications \
  -p '{"limit": 10}'

# Get insights
python mcp-client.py call -u http://localhost:8810 \
  -t facebook_get_page_insights \
  -p '{"metrics": ["page_impressions_unique", "page_reach", "page_post_engagements"]}'
```

## Troubleshooting

### Token Issues

**Error: "Invalid OAuth access token"**
- Token expired or revoked
- Solution: Generate new token from Graph API Explorer

**Error: "Missing permissions"**
- App doesn't have required permission
- Solution: Add permission in App Dashboard → App Review

**Error: "Token has expired"**
- Short-lived token expired (1 hour)
- Solution: Exchange for long-lived token (60 days)

### Permission Issues

**Error: "Permissions not granted"**
- User hasn't approved the permission
- Solution: Re-authorize with additional permissions

**Error: "App not approved for this action"**
- App in development mode, action requires review
- Solution: Submit app for review (for production use)

### API Issues

**Error: "Page not found"**
- Wrong Page ID or no access
- Solution: Verify Page ID, ensure you're admin

**Error: "Rate limit exceeded"**
- Too many API calls
- Solution: Wait and retry, reduce check interval

## App Review (For Production)

For production use with multiple users:

1. Go to **App Dashboard** → **App Review**
2. Click **Start Submission**
3. For each permission:
   - Provide use case description
   - Upload screencast showing permission usage
   - Explain how data will be used
4. Submit for review (takes 3-7 days)

### Sample Use Case Description

```
Our AI Employee application helps small business owners manage their 
social media presence. The app will:

1. Post business updates automatically based on business events
2. Monitor notifications for urgent customer inquiries
3. Track page insights to measure engagement
4. Respond to customer messages with AI-generated replies

All data is used locally and not stored externally. Users authenticate 
via OAuth and can revoke access at any time.
```

## Security Best Practices

1. **Never commit tokens to git**
   - Add `.env` to `.gitignore`
   - Use environment variables

2. **Rotate tokens regularly**
   - Regenerate every 60 days
   - Revoke unused tokens

3. **Use minimum required permissions**
   - Only request what you need
   - Review permissions quarterly

4. **Monitor API usage**
   - Check App Dashboard → Insights
   - Set up usage alerts

5. **Secure your App Secret**
   - Never share or expose
   - Regenerate if compromised

## Quick Reference

### Get Access Token URL

```
https://www.facebook.com/v19.0/dialog/oauth?
  client_id={app-id}&
  redirect_uri={redirect-uri}&
  scope=pages_manage_posts,pages_read_engagement,pages_messaging,user_notifications
```

### Graph API Endpoints

```
Base URL: https://graph.facebook.com/v19.0

User Profile: /me
Page Posts: /{page-id}/feed
Page Insights: /{page-id}/insights
Notifications: /me/notifications
Messages: /{page-id}/conversations
```

### Token Validation

```bash
curl "https://graph.facebook.com/v19.0/debug_token?
  input_token={your-token}&
  access_token={app-id}|{app-secret}"
```

## Resources

- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Guide](https://developers.facebook.com/docs/facebook-login/access-tokens)
- [App Review Guide](https://developers.facebook.com/docs/app-review)
- [Permission Reference](https://developers.facebook.com/docs/permissions)

---

*Facebook Graph API Integration - Gold Tier  
Uses official API (ToS compliant, no browser automation)*
