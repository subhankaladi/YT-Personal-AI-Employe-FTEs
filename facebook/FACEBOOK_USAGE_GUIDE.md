# Facebook Integration - Practical Usage Guide

Step-by-step guide for auto-posting and comment detection using Facebook Graph API.

## Prerequisites

✅ You've configured `facebook/.env` with your credentials:
```bash
FACEBOOK_APP_ID=your_app_id
FACEBOOK_APP_SECRET=your_app_secret
FACEBOOK_ACCESS_TOKEN=your_access_token
FACEBOOK_PAGE_ID=your_page_id
```

## Part 1: Testing Your Connection

### Step 1: Verify Token is Working

```bash
cd AI_Employee_Vault\scripts

# Test token verification
python facebook_graph_watcher.py ..\ --verify
```

**Expected Output:**
```
✓ Facebook access token is valid
```

**If you get an error:**
- Check your token in `facebook/.env`
- Make sure token hasn't expired (valid for 60 days)
- Regenerate from: https://developers.facebook.com/tools/explorer/

### Step 2: Test Basic Connection

```bash
# Test getting your profile/page info
python -c "
import sys
sys.path.append('../facebook')
from facebook_graph_mcp_server import facebook_client

# Get your info
me = facebook_client.get_me()
print('Connected as:', me.get('name', 'Unknown'))
print('ID:', me.get('id'))
"
```

**Expected Output:**
```
Connected as: Your Name or Page Name
ID: 123456789
```

---

## Part 2: Auto-Posting to Facebook

### Method 1: Using Qwen Code (Recommended)

Qwen Code can post to Facebook using the MCP server.

#### Step 1: Start Facebook MCP Server

Open a terminal:

```bash
cd facebook
python facebook_graph_mcp_server.py
```

Keep this terminal open (server running).

#### Step 2: Post Using Qwen Code

Open another terminal and use Qwen Code:

```bash
# Simple text post
qwen "Post to Facebook: Hello from AI Employee! This is an automated post from my Gold Tier system. #AI #Automation"
```

**Qwen will:**
1. Call the `facebook_create_post` MCP tool
2. Post appears on your Facebook timeline/Page
3. Show you the post ID

#### Step 3: Post with Link

```bash
qwen "Post to Facebook about our new consulting service with a link to https://example.com"
```

#### Step 4: Post with Photo

```bash
qwen "Create a photo post on Facebook with image from https://example.com/image.jpg and caption 'Check out our new office!'"
```

### Method 2: Using Python Script Directly

Create a test script `test_facebook_post.py`:

```python
import sys
import os
from pathlib import Path

# Add facebook folder to path
sys.path.append(str(Path(__file__).parent / 'facebook'))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('facebook/.env')

from facebook_graph_mcp_server import facebook_client

# Test posting
message = """
🤖 AI Employee Gold Tier - Test Post

This is an automated post from my AI Employee system!
Features:
✅ Odoo Integration
✅ Facebook Graph API
✅ Auto-posting
✅ Comment monitoring

#AIEmployee #GoldTier #Automation
"""

print("Posting to Facebook...")
result = facebook_client.create_post(message=message)

print(f"Post created! ID: {result.get('post_id')}")
print(f"View at: https://facebook.com/{result.get('post_id')}")
```

**Run it:**
```bash
python test_facebook_post.py
```

### Method 3: Using MCP Client Directly

```bash
# Post to Facebook
python .qwen/skills/browsing-with-playwright/scripts/mcp-client.py call ^
  -t facebook_create_post ^
  -p "{\"message\": \"Hello from AI Employee! #GoldTier\", \"privacy\": \"EVERYONE\"}"
```

---

## Part 3: Detecting Latest Comments

### How Comment Detection Works

The Facebook Graph API watcher monitors:
1. **Notifications** - When someone comments on your posts
2. **Post Comments** - Direct comment queries on specific posts
3. **Messages** - Private messages on your Page

### Step 1: Run the Facebook Watcher

```bash
cd AI_Employee_Vault\scripts

# Run watcher (checks every 5 minutes = 300 seconds)
python facebook_graph_watcher.py ..\ --interval 300
```

**What it does:**
- Checks for new notifications every 5 minutes
- Looks for keywords: `urgent`, `asap`, `invoice`, `payment`, `help`, `pricing`, `quote`
- Creates action files in `Needs_Action/` folder when important activity detected

### Step 2: Test Comment Detection

**In one terminal** - Start the watcher:
```bash
python facebook_graph_watcher.py ..\ --interval 60 --verbose
```

**In another terminal** - Test manual check:
```bash
python facebook_graph_watcher.py ..\ --test
```

**Expected Output:**
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
   Found 2 recent messages
     - Customer A: Hi, I need help with...
==================================================
✓ Test completed successfully
```

### Step 3: View Comments on Specific Post

Create `test_get_comments.py`:

```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'facebook'))

from dotenv import load_dotenv
load_dotenv('facebook/.env')

from facebook_graph_mcp_server import facebook_client

# First, get your recent posts
print("Getting recent posts...")
posts = facebook_client.get_posts(limit=5)

for i, post in enumerate(posts):
    print(f"\n{i+1}. Post ID: {post['id']}")
    print(f"   Message: {post['message'][:100]}...")
    print(f"   Likes: {post['likes']}, Comments: {post['comments']}")

# Get comments on most recent post
if posts:
    post_id = posts[0]['id']
    print(f"\nGetting comments on post: {post_id}")
    
    comments = facebook_client.get_comments(post_id, limit=10)
    
    print(f"\nFound {len(comments)} comments:")
    for comment in comments:
        print(f"  - {comment['from']}: {comment['message'][:50]}...")
```

**Run it:**
```bash
python test_get_comments.py
```

### Step 4: Auto-Respond to Comments

Create `auto_respond_comments.py`:

```python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / 'facebook'))

from dotenv import load_dotenv
load_dotenv('facebook/.env')

from facebook_graph_mcp_server import facebook_client

# Keywords that trigger auto-response
RESPONSE_KEYWORDS = ['help', 'question', 'pricing', 'quote', 'invoice', 'asap', 'urgent']

# Get recent posts
posts = facebook_client.get_posts(limit=3)

for post in posts:
    post_id = post['id']
    print(f"Checking comments on post: {post_id}")
    
    # Get comments
    comments = facebook_client.get_comments(post_id, limit=20)
    
    for comment in comments:
        message = comment['message'].lower()
        comment_id = comment['id']
        commenter = comment['from']
        
        # Check if comment needs response
        needs_response = any(keyword in message for keyword in RESPONSE_KEYWORDS)
        
        if needs_response:
            print(f"  ⚠️ Comment needs response: {commenter}")
            print(f"     Message: {comment['message']}")
            
            # Create action file for AI to process
            from datetime import datetime
            from pathlib import Path
            
            vault_path = Path(__file__).parent / 'AI_Employee_Vault' / 'Needs_Action'
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            action_file = vault_path / f'FACEBOOK_COMMENT_{timestamp}.md'
            action_file.write_text(f"""---
type: facebook_comment
post_id: {post_id}
comment_id: {comment_id}
from: {commenter}
received: {datetime.now().isoformat()}
priority: high
---

# Facebook Comment Needs Response

**Post ID:** {post_id}
**Comment ID:** {comment_id}
**From:** {commenter}
**Message:** {comment['message']}

## Suggested Actions
- [ ] Draft response using Qwen Code
- [ ] Post response using facebook_create_comment tool
- [ ] Follow up if needed

## Quick Response Command
```bash
qwen "Draft a helpful response to this Facebook comment: {comment['message']}"
```
""")
            
            print(f"     ✓ Created action file: {action_file}")
        else:
            print(f"  ✓ Comment (no action needed): {commenter}")
```

**Run it:**
```bash
python auto_respond_comments.py
```

---

## Part 4: Complete Auto-Posting Workflow

### Scenario: Post When New Item in Needs_Action

Create `post_on_action.py`:

```python
import sys
from pathlib import Path
import time

sys.path.append(str(Path(__file__).parent / 'facebook'))
sys.path.append(str(Path(__file__).parent / 'AI_Employee_Vault' / 'scripts'))

from dotenv import load_dotenv
load_dotenv('facebook/.env')

from facebook_graph_mcp_server import facebook_client
from pathlib import Path

vault_path = Path(__file__).parent / 'AI_Employee_Vault'
needs_action = vault_path / 'Needs_Action'
done_folder = vault_path / 'Done'

print("Monitoring Needs_Action folder for Facebook posts...")

while True:
    # Check for new action files
    action_files = list(needs_action.glob('*.md'))
    
    for action_file in action_files:
        content = action_file.read_text()
        
        # Check if it's a Facebook post request
        if 'facebook' in content.lower() and 'post' in content.lower():
            print(f"Found Facebook post request: {action_file.name}")
            
            # Extract post content (simplified - AI would do this better)
            # In practice, Qwen Code would process the file and create the post
            
            # For demo, create a simple post
            message = f"""
📢 New Business Update

Action item detected and processed.
File: {action_file.name}

#BusinessUpdate #AIEmployee
"""
            
            # Post to Facebook
            result = facebook_client.create_post(message=message)
            
            if result.get('success'):
                print(f"✓ Posted to Facebook! ID: {result.get('post_id')}")
                
                # Move to Done folder
                done_folder.mkdir(parents=True, exist_ok=True)
                action_file.rename(done_folder / action_file.name)
            else:
                print(f"✗ Post failed: {result.get('error')}")
    
    # Wait 30 seconds before checking again
    time.sleep(30)
```

**Run it:**
```bash
python post_on_action.py
```

**Then drop a file in `AI_Employee_Vault/Inbox/` with post content!**

---

## Part 5: Scheduled Auto-Posting

### Post Every Day at 9 AM

Create `scheduled_posts.py`:

```python
import schedule
import time
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent / 'facebook'))

from dotenv import load_dotenv
load_dotenv('facebook/.env')

from facebook_graph_mcp_server import facebook_client

# Post templates
MONDAY_POST = """
💼 Monday Motivation

Starting the week strong! Ready to help clients with:
✅ AI Automation
✅ Business Process Optimization  
✅ Digital Transformation

Have a great week ahead!

#MondayMotivation #Business #AI
"""

WEDNESDAY_POST = """
🚀 Wednesday Wisdom

"Automation is not about replacing people, it's about empowering them."

What are you automating this week?

#WednesdayWisdom #Automation #Productivity
"""

FRIDAY_POST = """
🎉 Friday Feature

This week we helped businesses:
- Automate customer responses
- Streamline invoice processing
- Generate automated reports

Ready to transform your business? Let's talk!

#FridayFeature #ClientSuccess #AI
"""

def post_to_facebook(content, post_name):
    """Post to Facebook"""
    print(f"Posting {post_name}...")
    result = facebook_client.create_post(message=content)
    
    if result.get('success'):
        print(f"✓ Posted! ID: {result.get('post_id')}")
    else:
        print(f"✗ Post failed: {result.get('error')}")

# Schedule posts
schedule.every().monday.at("09:00").do(post_to_facebook, MONDAY_POST, "Monday Post")
schedule.every().wednesday.at("09:00").do(post_to_facebook, WEDNESDAY_POST, "Wednesday Post")
schedule.every().friday.at("09:00").do(post_to_facebook, FRIDAY_POST, "Friday Post")

print("Scheduled Facebook Poster started!")
print("Posts scheduled:")
print("  - Monday 9:00 AM - Motivation")
print("  - Wednesday 9:00 AM - Wisdom")
print("  - Friday 9:00 AM - Feature")
print("\nPress Ctrl+C to stop")

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
```

**Run it:**
```bash
python scheduled_posts.py
```

**Or test immediately:**
```bash
python -c "
import sys
from pathlib import Path
sys.path.append('facebook')
from dotenv import load_dotenv
load_dotenv('facebook/.env')
from facebook_graph_mcp_server import facebook_client
result = facebook_client.create_post(message='Test post from scheduled poster!')
print(f'Posted: {result}')
"
```

---

## Part 6: Complete Workflow with Qwen Code

### Full Integration Example

**Step 1:** Start Facebook MCP Server
```bash
cd facebook
python facebook_graph_mcp_server.py
```

**Step 2:** Use Qwen Code for complete workflow

```bash
# Check notifications and draft responses
qwen "Check my Facebook notifications and draft responses to any customer inquiries"

# Create weekly content calendar
qwen "Create a week's worth of Facebook posts for my AI consulting business"

# Post the content
qwen "Post the first item from the content calendar to Facebook"

# Analyze engagement
qwen "Get my Facebook page insights and tell me which posts performed best"

# Monitor and respond to comments
qwen "Check comments on my recent posts and suggest responses to questions"
```

---

## Troubleshooting

### "Token Expired" Error

```bash
# Regenerate token from Graph API Explorer
# Visit: https://developers.facebook.com/tools/explorer/
# Get new token and update facebook/.env
```

### "Permissions Error"

Make sure you granted these permissions:
- `pages_manage_posts` - For posting
- `pages_read_engagement` - For insights
- `pages_read_user_content` - For comments
- `user_notifications` - For notifications

### "Page Not Found"

```bash
# Get your Page ID
python -c "
import sys
from pathlib import Path
sys.path.append('facebook')
from dotenv import load_dotenv
load_dotenv('facebook/.env')
from facebook_graph_mcp_server import facebook_client

result = facebook_client._make_request('me/accounts')
for page in result.get('data', []):
    print(f'Page: {page[\"name\"]}')
    print(f'ID: {page[\"id\"]}')
    print(f'Token: {page[\"access_token\"]}')
"
```

---

## Quick Reference Commands

```bash
# Verify token
python facebook_graph_watcher.py ..\ --verify

# Test connection
python facebook_graph_watcher.py ..\ --test

# Run watcher (continuous monitoring)
python facebook_graph_watcher.py ..\ --interval 300

# Start MCP server (for Qwen Code)
cd facebook && python facebook_graph_mcp_server.py

# Test post
python -c "from facebook_graph_mcp_server import facebook_client; print(facebook_client.create_post(message='Test!'))"

# Get recent posts
python -c "from facebook_graph_mcp_server import facebook_client; print(facebook_client.get_posts(5))"

# Get notifications
python -c "from facebook_graph_mcp_server import facebook_client; print(facebook_client.get_notifications(10))"
```

---

## Next Steps

1. **Test basic connection** - Verify token works
2. **Create test post** - Confirm posting works
3. **Run watcher** - Test comment detection
4. **Integrate with Qwen** - Use MCP server
5. **Set up scheduling** - Auto-post on schedule
6. **Monitor and refine** - Check insights regularly

For detailed API documentation, see [FACEBOOK_SETUP.md](FACEBOOK_SETUP.md)

---

*Facebook Graph API - Practical Usage Guide  
Gold Tier Integration*
