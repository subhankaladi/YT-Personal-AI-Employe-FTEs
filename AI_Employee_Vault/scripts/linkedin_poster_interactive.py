#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Interactive LinkedIn posting tool.

This version opens a VISIBLE browser that stays open, allowing you to:
- See what's happening
- Help with CAPTCHA if needed
- Manually intervene if LinkedIn blocks automation

Usage:
    python linkedin_poster_interactive.py --login  # First time login
    python linkedin_poster_interactive.py --post "Your post content"
"""

import sys
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import List

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install playwright")
    print("  playwright install chromium")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class LinkedInInteractivePoster:
    """Post to LinkedIn using visible interactive browser."""
    
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.browser = None
        self.page = None
        self.context = None
    
    def login(self):
        """Open LinkedIn for manual login - keeps browser open."""
        print("\n" + "="*60)
        print("LINKEDIN LOGIN")
        print("="*60)
        print("\nA browser window will open.")
        print("1. Log in to LinkedIn")
        print("2. Wait for your feed to load")
        print("3. Close the browser when done")
        print("\nSession will be saved for next time.\n")
        
        with sync_playwright() as p:
            # Launch VISIBLE browser
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,  # VISIBLE browser
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized'
                ],
                viewport={'width': 1280, 'height': 720}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            page.goto('https://www.linkedin.com/login')
            
            print("Waiting for you to log in...")
            print("Press Ctrl+C when done to close browser.\n")
            
            # Keep running until user closes
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nClosing browser...")
                browser.close()
                print("Login session saved!")
    
    def post(self, content: str, hashtags: List[str] = None, wait_time: int = 5):
        """
        Post to LinkedIn with visible browser.
        
        Args:
            content: Post content
            hashtags: List of hashtags
            wait_time: Seconds to wait between actions (human-like)
        """
        print("\n" + "="*60)
        print("POSTING TO LINKEDIN")
        print("="*60)
        print(f"\nContent: {content[:100]}...")
        if hashtags:
            print(f"Hashtags: {' '.join(hashtags)}")
        print()
        
        with sync_playwright() as p:
            # Launch VISIBLE browser with saved session
            print("Opening LinkedIn...")
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,  # VISIBLE so you can see what's happening
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized'
                ],
                viewport={'width': 1280, 'height': 720}
            )
            
            page = browser.pages[0] if browser.pages else browser.new_page()
            
            # Go to feed
            print("Navigating to LinkedIn feed...")
            page.goto('https://www.linkedin.com/feed/', wait_until='networkidle')
            
            # Wait for page to fully load
            print("Waiting for page to load...")
            time.sleep(wait_time)
            
            # Check if we're on feed page
            current_url = page.url
            if 'feed' not in current_url:
                print(f"\nWarning: Not on feed page. Current URL: {current_url}")
                print("You may need to log in again.")
                print("\nKeeping browser open for you to handle manually...")
                print("Close browser when done.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Try to find and click "Start a post"
            print("Looking for 'Start a post' button...")
            try:
                post_button = page.locator('[aria-label="Start a post"]').first
                post_button.click(timeout=10000)
                print("Clicked 'Start a post'")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Could not click 'Start a post': {e}")
                print("\nKeeping browser open for manual posting...")
                print("Type your post manually, then close browser.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Find the editor and type content
            print("Typing content...")
            try:
                editor = page.locator('.ql-editor[contenteditable="true"]').first
                
                # Prepare content with hashtags
                full_content = content
                if hashtags:
                    full_content += '\n\n' + ' '.join([f'#{tag}' for tag in hashtags])
                
                # Type slowly (human-like)
                editor.fill(full_content)
                print(f"Typed {len(full_content)} characters")
                time.sleep(wait_time)
                
            except Exception as e:
                print(f"Could not type content: {e}")
                print("\nKeeping browser open for manual posting...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Click Post button
            print("Looking for 'Post' button...")
            try:
                post_btn = page.locator('button:has-text("Post")').first
                post_btn.click(timeout=10000)
                print("Clicked 'Post' button")
                
                # Wait for success
                print("Waiting for confirmation...")
                time.sleep(wait_time)
                
                # Check if post was successful
                current_url = page.url
                if 'feed' in current_url:
                    print("\n✓ Post appears successful!")
                    print("Taking screenshot...")
                    
                    # Save screenshot
                    screenshot_path = Path.cwd().parent / 'Done' / f'linkedin_{int(time.time())}.png'
                    screenshot_path.parent.mkdir(exist_ok=True)
                    page.screenshot(path=str(screenshot_path))
                    print(f"Screenshot saved: {screenshot_path}")
                    
                    result = {'status': 'posted', 'screenshot': str(screenshot_path)}
                else:
                    print(f"\n? Post status uncertain. URL: {current_url}")
                    result = {'status': 'uncertain'}
                
            except Exception as e:
                print(f"Could not click Post: {e}")
                print("\nKeeping browser open for you to post manually...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            print("\nKeeping browser open for 10 seconds to verify...")
            time.sleep(10)
            
            browser.close()
            print("Browser closed.")
            
            return result


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Interactive Poster')
    parser.add_argument('--login', '-l', action='store_true',
                       help='Open LinkedIn for login (keeps browser open)')
    parser.add_argument('--post', '-p', help='Post content to LinkedIn')
    parser.add_argument('--hashtags', '-H', nargs='+', default=['AI', 'automation'],
                       help='Hashtags for post')
    parser.add_argument('--session', '-s', 
                       help='Session folder path (default: ./.linkedin_session)')
    parser.add_argument('--wait', '-w', type=int, default=5,
                       help='Wait time between actions in seconds')
    
    args = parser.parse_args()
    
    session_path = Path(args.session) if args.session else Path.cwd().parent / '.linkedin_session'
    
    poster = LinkedInInteractivePoster(str(session_path))
    
    if args.login:
        poster.login()
    
    elif args.post:
        result = poster.post(args.post, args.hashtags, args.wait)
        print(f"\nResult: {result['status']}")
        if result.get('screenshot'):
            print(f"Screenshot: {result['screenshot']}")
    
    else:
        parser.print_help()
        print("\n\nExamples:")
        print("  # First time: Login to LinkedIn")
        print("  python linkedin_poster_interactive.py --login")
        print()
        print("  # Post to LinkedIn")
        print("  python linkedin_poster_interactive.py --post 'Hello LinkedIn!' --hashtags AI tech")
        print()
        print("  # Post with longer wait time (if LinkedIn is slow)")
        print("  python linkedin_poster_interactive.py --post 'Hello!' --wait 10")


if __name__ == '__main__':
    main()
