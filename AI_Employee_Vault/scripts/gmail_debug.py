#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher DEBUG - Test and debug Gmail queries.

Use this to see what emails are being found and why.
"""

import sys
import base64
import pickle
import argparse
from pathlib import Path
from datetime import datetime

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)


def get_service(credentials_path: str, token_path: str):
    """Get authenticated Gmail service."""
    if not Path(token_path).exists():
        print("Token not found. Run with --authenticate first.")
        return None
    
    creds = pickle.loads(Path(token_path).read_bytes())
    
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(None)
            with open(token_path, 'wb') as f:
                pickle.dump(creds, f)
        else:
            print("Credentials invalid. Re-authenticate.")
            return None
    
    return build('gmail', 'v1', credentials=creds)


def list_emails(service, query: str, max_results: int = 10):
    """List emails matching query."""
    print(f"\nQuery: {query}")
    print("-" * 60)
    
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("No emails found.\n")
        return []
    
    print(f"Found {len(messages)} emails:\n")
    
    for msg in messages:
        detail = service.users().messages().get(
            userId='me', id=msg['id'], format='metadata',
            metadataHeaders=['from', 'to', 'subject', 'date']
        ).execute()
        
        headers = {h['name']: h['value'] for h in detail['payload']['headers']}
        
        print(f"ID: {msg['id']}")
        print(f"  From: {headers.get('From', 'N/A')}")
        print(f"  To: {headers.get('To', 'N/A')}")
        print(f"  Subject: {headers.get('Subject', 'N/A')}")
        print(f"  Date: {headers.get('Date', 'N/A')}")
        print()
    
    return messages


def test_queries(service):
    """Test different Gmail queries to see what works."""
    print("\n" + "="*60)
    print("TESTING GMAIL QUERIES")
    print("="*60)
    
    queries = [
        ("All unread", "is:unread"),
        ("All important", "is:important"),
        ("Unread + Important", "is:unread is:important"),
        ("From you", "from:me"),
        ("To subhankaladi2", "to:subhankaladi2@gmail.com"),
        ("Recent (within 1 day)", "newer_than:1d"),
        ("Unread + Recent", "is:unread newer_than:1d"),
        ("All recent unread important", "is:unread is:important newer_than:1d"),
    ]
    
    for name, query in queries:
        print(f"\n[{name}]")
        list_emails(service, query, max_results=5)


def main():
    parser = argparse.ArgumentParser(description='Gmail Watcher DEBUG')
    parser.add_argument('--credentials', '-c', default='../../credentials.json',
                       help='Path to OAuth credentials JSON')
    parser.add_argument('--token', '-t', default='../.gmail_token.pkl',
                       help='Path to token file')
    parser.add_argument('--query', '-q', help='Test specific query')
    parser.add_argument('--test', action='store_true',
                       help='Run all test queries')
    parser.add_argument('--list', action='store_true',
                       help='List recent emails')
    
    args = parser.parse_args()
    
    credentials_path = Path(args.credentials)
    token_path = Path(args.token)
    
    if not credentials_path.exists():
        print(f"Credentials not found: {credentials_path}")
        sys.exit(1)
    
    service = get_service(str(credentials_path), str(token_path))
    if not service:
        sys.exit(1)
    
    print("Gmail Watcher DEBUG")
    print("="*60)
    
    if args.test:
        test_queries(service)
    
    elif args.query:
        list_emails(service, args.query)
    
    elif args.list:
        print("\nRecent emails:")
        list_emails(service, 'newer_than:1d', max_results=10)
    
    else:
        # Default: show help
        parser.print_help()
        print("\n\nExamples:")
        print("  # Test all queries to see what's found")
        print("  python gmail_debug.py --test")
        print()
        print("  # Test specific query")
        print("  python gmail_debug.py --query \"is:unread\"")
        print()
        print("  # List recent emails")
        print("  python gmail_debug.py --list")
        print()
        print("  # Find emails to specific address")
        print('  python gmail_debug.py --query "to:subhankaladi2@gmail.com"')


if __name__ == '__main__':
    main()
