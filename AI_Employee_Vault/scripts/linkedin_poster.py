#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Auto-Poster - Create and post updates to LinkedIn.

WARNING: This uses LinkedIn automation which may violate LinkedIn's Terms of Service.
Use at your own risk and only for personal accounts.
Consider using LinkedIn Marketing API for business pages.

Usage:
    python linkedin_poster.py /path/to/vault --post "Your post content"
    python linkedin_poster.py /path/to/vault --draft  # Create for approval
"""

import sys
import time
import logging
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

# Import base watcher from same directory
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class LinkedInPoster:
    """Post updates to LinkedIn using browser automation."""
    
    def __init__(self, vault_path: str, session_path: str,
                 email: str = "", password: str = "",
                 require_approval: bool = True, dry_run: bool = False):
        """
        Initialize LinkedIn Poster.
        
        Args:
            vault_path: Path to Obsidian vault
            session_path: Path to save browser session
            email: LinkedIn email (optional if session exists)
            password: LinkedIn password (optional if session exists)
            require_approval: Require approval before posting
            dry_run: If True, don't actually post
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)
        self.email = email
        self.password = password
        self.require_approval = require_approval
        self.dry_run = dry_run
        
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        # Ensure directories exist
        for folder in [self.needs_action, self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def authenticate(self) -> bool:
        """
        Authenticate with LinkedIn (save session).
        
        Returns:
            True if successful
        """
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=False,  # Show browser for QR/login
                    args=['--disable-blink-features=AutomationControlled']
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://www.linkedin.com/login')
                
                self.logger.info("Please log in to LinkedIn manually...")
                self.logger.info("Session will be saved for future use.")
                
                # Wait for user to log in (max 5 minutes)
                try:
                    page.wait_for_url('https://www.linkedin.com/feed/*', timeout=300000)
                    self.logger.info("Login detected!")
                    time.sleep(2)  # Let session fully load
                    browser.close()
                    return True
                except PlaywrightTimeout:
                    self.logger.warning("Login timeout. Try again.")
                    browser.close()
                    return False
                    
        except Exception as e:
            self.logger.error(f"Authentication error: {e}")
            return False
    
    def post_update(self, content: str, hashtags: List[str] = None,
                    screenshot: bool = True) -> Dict:
        """
        Post update to LinkedIn.
        
        Args:
            content: Post content
            hashtags: List of hashtags (without #)
            screenshot: Take screenshot after posting
            
        Returns:
            Dict with post result
        """
        result = {'status': 'unknown', 'content': content}
        
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post: {content[:100]}...")
            result['status'] = 'dry_run'
            return result
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ],
                    viewport={'width': 1280, 'height': 720}
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to feed
                self.logger.debug("Navigating to LinkedIn feed...")
                page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
                
                # Wait for post creation box
                try:
                    page.wait_for_selector('[aria-label="Start a post"]', timeout=30000)
                    self.logger.debug("Feed loaded")
                except PlaywrightTimeout:
                    self.logger.error("Feed did not load. May need to re-authenticate.")
                    browser.close()
                    result['status'] = 'auth_error'
                    return result
                
                # Small delay to appear human
                time.sleep(2)
                
                # Click "Start a post"
                self.logger.debug("Clicking 'Start a post'...")
                page.click('[aria-label="Start a post"]')
                
                # Wait for post dialog
                page.wait_for_selector('.ql-editor', timeout=10000)
                time.sleep(1)
                
                # Prepare content with hashtags
                full_content = content
                if hashtags:
                    hashtag_str = ' '.join([f'#{tag}' for tag in hashtags])
                    full_content = f"{content}\n\n{hashtag_str}"
                
                # Type content
                self.logger.debug("Typing content...")
                page.fill('.ql-editor', full_content)
                
                # Human-like delay
                time.sleep(2)
                
                # Click "Post" button
                self.logger.debug("Clicking 'Post'...")
                post_button = page.locator('button:has-text("Post")').first
                post_button.click()
                
                # Wait for success toast
                try:
                    page.wait_for_selector('.post-updated-toast, .toast', timeout=10000)
                    self.logger.info("Post successful!")
                    result['status'] = 'posted'
                    result['timestamp'] = datetime.now().isoformat()
                except PlaywrightTimeout:
                    self.logger.warning("Post confirmation not detected")
                    result['status'] = 'uncertain'
                
                # Take screenshot
                if screenshot and result['status'] == 'posted':
                    screenshot_path = self.done / f'linkedin_{int(time.time())}.png'
                    page.screenshot(path=str(screenshot_path))
                    result['screenshot'] = str(screenshot_path)
                    self.logger.info(f"Screenshot saved: {screenshot_path.name}")
                
                browser.close()
                
        except Exception as e:
            self.logger.error(f"Error posting: {e}")
            result['status'] = 'error'
            result['error'] = str(e)
        
        return result
    
    def create_approval_file(self, content: str, hashtags: List[str] = None,
                             scheduled_time: str = None) -> Path:
        """
        Create approval request file.
        
        Args:
            content: Post content
            hashtags: List of hashtags
            scheduled_time: Optional scheduled time ISO format
            
        Returns:
            Path to created file
        """
        timestamp = datetime.now().isoformat()
        filename = f'LINKEDIN_POST_{int(time.time())}.md'
        
        hashtag_str = ' '.join([f'#{tag}' for tag in (hashtags or [])])
        
        file_content = f'''---
type: linkedin_post
content_preview: {content[:50]}...
hashtags: {hashtag_str}
created: {timestamp}
scheduled: {scheduled_time or 'immediate'}
status: pending_approval
---

# LinkedIn Post Preview

## Content

{content}

## Hashtags

{hashtag_str}

## Scheduled

{scheduled_time or 'Immediate posting upon approval'}

---

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with comments.

---
*Generated by LinkedIn Auto-Poster v0.1 (Silver Tier)*

**Note:** Posting frequency should be limited to 1-2 posts per day for best engagement and ToS compliance.
'''
        filepath = self.pending_approval / filename
        filepath.write_text(file_content)
        
        self.logger.info(f"Created approval file: {filename}")
        return filepath
    
    def process_approved_posts(self) -> List[Dict]:
        """
        Process all approved posts in /Approved folder.
        
        Returns:
            List of post results
        """
        results = []
        
        for filepath in self.approved.glob('LINKEDIN_POST_*.md'):
            self.logger.info(f"Processing approved post: {filepath.name}")
            
            # Read file
            content = filepath.read_text()
            
            # Parse frontmatter (simple extraction)
            post_content = self._extract_content(content)
            hashtags = self._extract_hashtags(content)
            
            # Post
            result = self.post_update(post_content, hashtags)
            result['file'] = str(filepath)
            results.append(result)
            
            # Move to Done or back to Pending
            if result['status'] in ['posted', 'dry_run']:
                dest = self.done / filepath.name
                filepath.rename(dest)
                self.logger.info(f"Moved to Done: {dest.name}")
            else:
                dest = self.pending_approval / filepath.name
                filepath.rename(dest)
                self.logger.warning(f"Post failed, moved back: {dest.name}")
        
        return results
    
    def _extract_content(self, markdown: str) -> str:
        """Extract post content from markdown file."""
        lines = markdown.split('\n')
        in_content = False
        content_lines = []
        
        for line in lines:
            if line.startswith('## Content'):
                in_content = True
                continue
            if in_content:
                if line.startswith('## '):
                    break
                if line.strip() and not line.startswith('---'):
                    content_lines.append(line)
        
        return '\n'.join(content_lines).strip()
    
    def _extract_hashtags(self, markdown: str) -> List[str]:
        """Extract hashtags from markdown file."""
        import re
        # Look for hashtags in frontmatter
        match = re.search(r'hashtags:\s*(.+)', markdown)
        if match:
            hashtag_str = match.group(1).strip()
            # Remove # symbols and split
            hashtags = [tag.strip().lstrip('#') for tag in hashtag_str.split()]
            return hashtags
        return []
    
    def generate_post_content(self, topic: str, tone: str = 'professional') -> str:
        """
        Generate post content from topic (simple template-based).
        
        Args:
            topic: Topic to post about
            tone: 'professional', 'casual', or 'enthusiastic'
            
        Returns:
            Generated post content
        """
        templates = {
            'professional': [
                f"Sharing insights on {topic}. Key takeaways:\n\n"
                "• Industry trends are evolving\n"
                "• New opportunities emerging\n"
                "• Adaptation is crucial\n\n"
                "What are your thoughts?",
                
                f"Just completed analysis on {topic}. Here's what we found:\n\n"
                "The data reveals interesting patterns that businesses should note.\n\n"
                "Happy to discuss further in the comments."
            ],
            'casual': [
                f"Been diving deep into {topic} lately. Here's what I learned... 🧵\n\n"
                "Sometimes the best insights come from unexpected places.\n\n"
                "What's your experience been?",
                
                f"Quick thought on {topic}:\n\n"
                "It's not just about working harder, it's about working smarter.\n\n"
                "Agree or disagree?"
            ],
            'enthusiastic': [
                f"Exciting developments in {topic}! 🚀\n\n"
                "This is a game-changer for the industry.\n\n"
                "Can't wait to see what happens next!\n\n"
                "#innovation #growth #business",
                
                f"Big news about {topic}! 🎉\n\n"
                "We've been working hard on this and the results speak for themselves.\n\n"
                "Stay tuned for more updates!"
            ]
        }
        
        import random
        return random.choice(templates.get(tone, templates['professional']))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Auto-Poster')
    parser.add_argument('vault_path', help='Path to Obsidian vault')
    parser.add_argument('--post', '-p', help='Post content directly')
    parser.add_argument('--draft', '-d', action='store_true', help='Create draft for approval')
    parser.add_argument('--topic', '-t', help='Generate post from topic')
    parser.add_argument('--tone', default='professional',
                       choices=['professional', 'casual', 'enthusiastic'],
                       help='Tone for generated content')
    parser.add_argument('--hashtags', '-H', nargs='+', help='Hashtags (without #)')
    parser.add_argument('--session', '-s', help='Path to session folder')
    parser.add_argument('--email', '-e', help='LinkedIn email')
    parser.add_argument('--password', '-P', help='LinkedIn password (use env var instead)')
    parser.add_argument('--authenticate', '-a', action='store_true', help='Run authentication')
    parser.add_argument('--dry-run', action='store_true', help='Don\'t actually post')
    parser.add_argument('--process-approved', action='store_true', help='Process approved posts')
    parser.add_argument('--config', '-c', help='Path to config JSON file')
    
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    # Load config
    config = {}
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config = json.loads(config_path.read_text())
    
    # Session path
    session_path = Path(args.session) if args.session else config.get('session_path', Path.home() / '.linkedin_session')
    
    # Credentials
    email = args.email or config.get('email', '')
    password = args.password or config.get('password_env')
    if password and password.endswith('_ENV'):
        password = ''  # Would need to read from env
    
    # Create poster
    poster = LinkedInPoster(
        str(vault_path),
        str(session_path),
        email=email,
        password=password or '',
        require_approval=config.get('require_approval', True),
        dry_run=args.dry_run
    )
    
    if args.authenticate:
        print("Starting LinkedIn authentication...")
        if poster.authenticate():
            print("\n✓ Authentication successful!")
            print("Session saved. You can now post without re-authenticating.")
        else:
            print("\n✗ Authentication failed")
            sys.exit(1)
    
    elif args.process_approved:
        print("Processing approved posts...")
        results = poster.process_approved_posts()
        for result in results:
            print(f"  {result['file']}: {result['status']}")
    
    elif args.topic:
        content = poster.generate_post_content(args.topic, args.tone)
        hashtags = args.hashtags or config.get('hashtags', ['business', 'insights'])
        
        if args.draft:
            filepath = poster.create_approval_file(content, hashtags)
            print(f"\n✓ Draft created: {filepath.name}")
            print("Move to /Approved to post, /Rejected to cancel.")
        else:
            result = poster.post_update(content, hashtags)
            print(f"\nPost result: {result['status']}")
    
    elif args.post:
        hashtags = args.hashtags or config.get('hashtags', [])
        
        if args.draft:
            filepath = poster.create_approval_file(args.post, hashtags)
            print(f"\n✓ Draft created: {filepath.name}")
        else:
            result = poster.post_update(args.post, hashtags)
            print(f"\nPost result: {result['status']}")
    
    else:
        parser.print_help()
        print("\nExamples:")
        print("  # Authenticate first time")
        print("  python linkedin_poster.py ./vault --authenticate")
        print()
        print("  # Create draft for approval")
        print("  python linkedin_poster.py ./vault --post 'Hello LinkedIn!' --draft")
        print()
        print("  # Generate and post immediately")
        print("  python linkedin_poster.py ./vault --topic 'AI trends' --tone enthusiastic")
        print()
        print("  # Process approved posts")
        print("  python linkedin_poster.py ./vault --process-approved")


if __name__ == '__main__':
    main()
