# Facebook Graph API Integration - Gold Tier

Official Facebook integration using the Facebook Graph API for posting and monitoring.

## Overview

This integration uses the **official Facebook Graph API** instead of browser automation (Playwright). This approach provides:

| Feature | Graph API | Browser Automation |
|---------|-----------|-------------------|
| ToS Compliance | ✅ Official API | ⚠️ May violate ToS |
| Reliability | ✅ Stable API | ⚠️ UI changes break it |
| Account Safety | ✅ No risk | ⚠️ Restriction risk |
| Features | ✅ Full access | ⚠️ Limited to UI |
| Authentication | ✅ OAuth | ⚠️ Session cookies |
| Rate Limiting | ✅ Documented | ⚠️ Unknown |

## Quick Start

### 1. Create Facebook App

Visit: https://developers.facebook.com/apps/
- Create new app (Business type)
- Note App ID and App Secret

### 2. Get Access Token

Visit: https://developers.facebook.com/tools/explorer/
- Select your app
- Get Token → Get User Access Token
- Select permissions (see below)
- Generate and copy token

### 3. Configure Environment

Create `facebook\.env`:

```bash
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
```

### 4. Test Integration

```bash
# Verify token
python facebook_graph_mcp_server.py

# Test watcher
python facebook_graph_watcher.py /path/to/vault --test
```

## Required Permissions

For full functionality, request these permissions during token generation:

| Permission | Purpose | Required For |
|------------|---------|--------------|
| `pages_manage_posts` | Create posts | Posting to Page |
| `pages_read_engagement` | Read insights | Analytics |
| `pages_read_user_content` | Read comments/messages | Monitoring |
| `pages_messaging` | Send/receive messages | Customer support |
| `user_notifications` | Read notifications | Alert monitoring |
| `publish_to_groups` | Post to groups | Community management |

## Components

### 1. Facebook Graph MCP Server

**File:** `facebook_graph_mcp_server.py`

MCP server providing Facebook tools to Qwen Code.

**Tools:**
- `facebook_verify_token` - Verify token validity
- `facebook_get_me` - Get user/page info
- `facebook_create_post` - Create text post
- `facebook_create_photo_post` - Create photo post
- `facebook_get_posts` - Get recent posts
- `facebook_get_notifications` - Get notifications
- `facebook_get_page_insights` - Get analytics
- `facebook_get_comments` - Get post comments
- `facebook_create_comment` - Comment on post
- `facebook_get_messages` - Get Page messages
- `facebook_generate_hashtags` - Generate hashtags

**Start Server:**
```bash
cd facebook
python facebook_graph_mcp_server.py
```

### 2. Facebook Graph Watcher

**File:** `AI_Employee_Vault/scripts/facebook_graph_watcher.py`

Continuous monitoring watcher for Facebook notifications and messages.

**Features:**
- Checks notifications every 5 minutes
- Filters by keywords (urgent, invoice, payment, etc.)
- Creates action files in Needs_Action folder
- Monitors Page messages (if Page ID configured)

**Usage:**
```bash
# Verify token
python facebook_graph_watcher.py /path/to/vault --verify

# Test check
python facebook_graph_watcher.py /path/to/vault --test

# Run continuous
python facebook_graph_watcher.py /path/to/vault --interval 300
```

## Setup Guide

For detailed setup instructions, see [FACEBOOK_SETUP.md](FACEBOOK_SETUP.md).

### Quick Setup Steps

1. **Create Facebook App**
   - Go to https://developers.facebook.com/apps/
   - Create app (Business type)
   - Complete app setup

2. **Get Access Token**
   - Use Graph API Explorer
   - Request required permissions
   - Generate token

3. **Get Page Access Token** (for business features)
   - Query: `/me/accounts`
   - Copy page access token and ID

4. **Configure Environment**
   - Create `.env` file
   - Add credentials
   - Don't commit to git!

5. **Test Integration**
   - Verify token
   - Test notifications
   - Test posting

## Usage Examples

### Post to Facebook

```bash
# Using Qwen Code
qwen "Post to Facebook: Excited to announce our new AI consulting service! #AI #Business"
```

### Check Notifications

```bash
# Using Qwen Code
qwen "Check my Facebook notifications for any urgent customer inquiries"
```

### Get Page Insights

```bash
# Using Qwen Code
qwen "Get my Facebook page insights for reach and engagement metrics"
```

### Monitor and Respond

```bash
# Run watcher (continuous monitoring)
python facebook_graph_watcher.py /path/to/vault --interval 300

# Watcher creates action files for important notifications
# Qwen Code processes them and drafts responses
```

## API Reference

### Graph API Endpoints

```
Base URL: https://graph.facebook.com/v19.0

User Profile:    /me
Page Posts:      /{page-id}/feed
Page Insights:   /{page-id}/insights
Notifications:   /me/notifications
Messages:        /{page-id}/conversations
Post Comments:   /{post-id}/comments
```

### Access Token Types

| Type | Validity | Use Case |
|------|----------|----------|
| User Token | 1-2 hours | Testing |
| Long-lived User Token | 60 days | Production |
| Page Token | Never expires | Page management |

### Getting Long-lived Token

```bash
curl -G "https://graph.facebook.com/v19.0/oauth/access_token" \
  -d "grant_type=fb_exchange_token" \
  -d "client_id=YOUR_APP_ID" \
  -d "client_secret=YOUR_APP_SECRET" \
  -d "fb_exchange_token=SHORT_LIVED_TOKEN"
```

## Troubleshooting

### Common Errors

**"Invalid OAuth access token"**
- Token expired or revoked
- Solution: Generate new token

**"Missing permissions"**
- App doesn't have required permission
- Solution: Add permission in App Dashboard → App Review

**"Error validating application"**
- App ID or Secret incorrect
- Solution: Verify credentials in .env

**"Page not found"**
- Wrong Page ID or no access
- Solution: Verify Page ID, ensure you're admin

### Token Validation

```bash
curl "https://graph.facebook.com/v19.0/debug_token?
  input_token={your-token}&
  access_token={app-id}|{app-secret}"
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
   - Review quarterly

4. **Monitor API usage**
   - Check App Dashboard → Insights
   - Set up alerts

5. **Secure App Secret**
   - Never share or expose
   - Regenerate if compromised

## Rate Limits

Facebook Graph API has rate limits:

| Endpoint | Limit | Window |
|----------|-------|--------|
| User posts | 200 | 1 hour |
| Page posts | 200 | 1 hour |
| Notifications | 200 | 1 hour |
| Messages | 200 | 1 hour |
| Insights | 200 | 1 hour |

Our watcher checks every 5 minutes (12 times/hour), well within limits.

## App Review (Production)

For production use with multiple users:

1. Go to App Dashboard → App Review
2. Submit for review with:
   - Use case description
   - Screencast demonstration
   - Data usage explanation
3. Wait 3-7 days for approval

See [FACEBOOK_SETUP.md](FACEBOOK_SETUP.md) for detailed review guide.

## Files in This Folder

```
facebook/
├── facebook_graph_mcp_server.py  # MCP server
├── facebook_graph_watcher.py     # (in AI_Employee_Vault/scripts)
├── FACEBOOK_SETUP.md             # Detailed setup guide
├── .env.example                  # Environment template
└── README.md                     # This file
```

## Resources

- [Facebook Graph API Docs](https://developers.facebook.com/docs/graph-api)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Guide](https://developers.facebook.com/docs/facebook-login/access-tokens)
- [App Review Guide](https://developers.facebook.com/docs/app-review)
- [Permission Reference](https://developers.facebook.com/docs/permissions)

## Support

For issues or questions:
1. Check [FACEBOOK_SETUP.md](FACEBOOK_SETUP.md)
2. Review Facebook API documentation
3. Check Gold Tier documentation

---

*Facebook Graph API Integration - Gold Tier  
Uses official Facebook Graph API (ToS compliant)*
