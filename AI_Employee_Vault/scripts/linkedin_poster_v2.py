#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Poster - Interactive LinkedIn posting tool with better selectors.

This version tries multiple selectors to find the post button.
"""

import sys
import time
import logging
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


class LinkedInPoster:
    """Post to LinkedIn using visible browser with multiple selector attempts."""
    
    def __init__(self, session_path: str):
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
    
    def post(self, content: str, hashtags: List[str] = None, wait_time: int = 3):
        """
        Post to LinkedIn with visible browser.
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
                headless=False,
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
            
            # Take a screenshot for debugging
            debug_screenshot = Path.cwd().parent / 'Done' / f'linkedin_debug_{int(time.time())}.png'
            debug_screenshot.parent.mkdir(exist_ok=True)
            page.screenshot(path=str(debug_screenshot))
            print(f"Debug screenshot saved: {debug_screenshot}")
            
            # Check if we're on feed page
            current_url = page.url
            print(f"Current URL: {current_url}")
            if 'feed' not in current_url and 'linkedin' not in current_url.lower():
                print(f"\nWarning: Not on LinkedIn feed page.")
                print("Keeping browser open for you to handle manually...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Try multiple selectors for "Start a post"
            post_button_selectors = [
                '[aria-label="Start a post"]',
                'button:has-text("Start a post")',
                '.share-box-feed-entry__trigger',
                '[data-test-id="share-box-feed-entry-trigger"]',
                'button:has-text("Start")',
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    print(f"Trying selector: {selector}")
                    post_button = page.locator(selector).first
                    post_button.wait_for(state='visible', timeout=5000)
                    print(f"✓ Found with selector: {selector}")
                    break
                except Exception as e:
                    print(f"  ✗ Not found: {selector}")
                    continue
            
            if not post_button:
                print("\nCould not find 'Start a post' button with any selector.")
                print("\nKeeping browser open for manual posting...")
                print("Please click 'Start a post' manually, type your post, and close browser.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Click the button
            try:
                post_button.click(timeout=5000)
                print("Clicked 'Start a post'")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Could not click: {e}")
                print("\nKeeping browser open...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Try to find the editor
            print("Looking for text editor...")
            editor_selectors = [
                '.ql-editor[contenteditable="true"]',
                '.editor[contenteditable="true"]',
                '[data-test-id="share-box-inline-editor"]',
                'div[contenteditable="true"]',
            ]
            
            editor = None
            for selector in editor_selectors:
                try:
                    print(f"Trying editor selector: {selector}")
                    editor = page.locator(selector).first
                    editor.wait_for(state='visible', timeout=3000)
                    print(f"✓ Found editor with selector: {selector}")
                    break
                except Exception:
                    continue
            
            if not editor:
                print("\nCould not find text editor.")
                print("Keeping browser open for manual posting...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Prepare and type content
            full_content = content
            if hashtags:
                full_content += '\n\n' + ' '.join([f'#{tag}' for tag in hashtags])
            
            print(f"Typing {len(full_content)} characters...")
            try:
                editor.fill(full_content)
                print("Content typed successfully")
                time.sleep(wait_time)
            except Exception as e:
                print(f"Could not type content: {e}")
                print("Keeping browser open for manual posting...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            # Click Post button
            print("Looking for 'Post' button...")
            post_btn_selectors = [
                'button:has-text("Post")',
                'button:has-text("Post")',
                '.share-actions__primary-action',
                '[aria-label="Post"]',
            ]
            
            post_btn = None
            for selector in post_btn_selectors:
                try:
                    post_btn = page.locator(selector).first
                    post_btn.wait_for(state='visible', timeout=3000)
                    print(f"✓ Found Post button with selector: {selector}")
                    break
                except Exception:
                    continue
            
            if post_btn:
                try:
                    post_btn.click()
                    print("Clicked 'Post' button")
                    time.sleep(wait_time * 2)
                    
                    # Check result
                    print("Checking if post was successful...")
                    time.sleep(3)
                    
                    # Take success screenshot
                    success_screenshot = Path.cwd().parent / 'Done' / f'linkedin_success_{int(time.time())}.png'
                    page.screenshot(path=str(success_screenshot))
                    print(f"Success screenshot: {success_screenshot}")
                    
                    print("\n✓ Post completed!")
                    result = {'status': 'posted', 'screenshot': str(success_screenshot)}
                    
                except Exception as e:
                    print(f"Could not click Post: {e}")
                    print("Keeping browser open for manual posting...")
                    try:
                        while True:
                            time.sleep(1)
                    except KeyboardInterrupt:
                        browser.close()
                    return {'status': 'manual_intervention'}
            else:
                print("Could not find Post button.")
                print("Keeping browser open for you to post manually...")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    browser.close()
                return {'status': 'manual_intervention'}
            
            print("\nClosing browser in 5 seconds...")
            time.sleep(5)
            browser.close()
            
            return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description='LinkedIn Poster')
    parser.add_argument('--post', '-p', help='Post content to LinkedIn')
    parser.add_argument('--hashtags', '-H', nargs='+', default=['AI', 'automation'],
                       help='Hashtags for post')
    parser.add_argument('--session', '-s', 
                       help='Session folder path')
    parser.add_argument('--wait', '-w', type=int, default=3,
                       help='Wait time between actions in seconds')
    
    args = parser.parse_args()
    
    session_path = Path(args.session) if args.session else Path.cwd().parent / '.linkedin_session'
    
    poster = LinkedInPoster(str(session_path))
    
    if args.post:
        result = poster.post(args.post, args.hashtags, args.wait)
        print(f"\nResult: {result['status']}")
        if result.get('screenshot'):
            print(f"Screenshot: {result['screenshot']}")
    else:
        parser.print_help()
        print("\n\nExample:")
        print("  python linkedin_poster_v2.py --post 'Hello LinkedIn!' --hashtags AI tech")


if __name__ == '__main__':
    main()
