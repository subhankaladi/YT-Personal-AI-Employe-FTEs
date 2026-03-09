#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Send Email via MCP - Simple script to send emails through Email MCP Server.

Usage:
    python send_email.py --to recipient@example.com --subject "Hello" --body "Message"
"""

import sys
import logging
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from email_mcp_server import EmailMCPServer
except ImportError:
    print("Error: Could not import EmailMCPServer")
    print("Make sure email_mcp_server.py is in the same directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def send_email(to: str, subject: str, body: str, 
               attachments: list = None,
               credentials_path: str = None,
               token_path: str = None,
               dry_run: bool = False):
    """
    Send email using Email MCP Server.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body text
        attachments: List of attachment file paths (optional)
        credentials_path: Path to OAuth credentials JSON
        token_path: Path to token file
        dry_run: If True, log but don't send
    
    Returns:
        dict with result status
    """
    # Default paths
    if credentials_path is None:
        credentials_path = Path.cwd().parent.parent / 'credentials.json'
    else:
        credentials_path = Path(credentials_path)
    
    if token_path is None:
        token_path = Path.home() / '.email_token.pkl'
    else:
        token_path = Path(token_path)
    
    # Check credentials exist
    if not credentials_path.exists():
        print(f"Error: Credentials file not found: {credentials_path}")
        print("Please provide --credentials path")
        return {'status': 'error', 'error': 'Credentials not found'}
    
    # Check token exists
    if not token_path.exists():
        print(f"Error: Token file not found: {token_path}")
        print("Please authenticate first:")
        print(f"  python email_mcp_server.py --authenticate --credentials {credentials_path}")
        return {'status': 'error', 'error': 'Not authenticated'}
    
    # Create server
    server = EmailMCPServer(
        str(credentials_path),
        str(token_path),
        dry_run=dry_run
    )
    
    # Send email
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Sending email...")
    print(f"  To: {to}")
    print(f"  Subject: {subject}")
    print(f"  Body: {body[:100]}{'...' if len(body) > 100 else ''}")
    if attachments:
        print(f"  Attachments: {', '.join(attachments)}")
    print()
    
    try:
        result = server.send_email(
            to=to,
            subject=subject,
            body=body,
            attachments=attachments
        )
        
        if result.get('status') == 'sent' or result.get('dry_run'):
            print(f"[OK] Email sent successfully!")
            print(f"  Message ID: {result.get('id', 'N/A')}")
            print(f"  Thread ID: {result.get('thread_id', 'N/A')}")
            return result
        else:
            print(f"[ERROR] Email send failed: {result}")
            return result
            
    except Exception as e:
        print(f"[ERROR] Error sending email: {e}")
        return {'status': 'error', 'error': str(e)}


def main():
    parser = argparse.ArgumentParser(
        description='Send Email via MCP Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Send simple email
  python send_email.py --to user@example.com --subject "Hello" --body "Hi there!"

  # Send with attachments
  python send_email.py --to user@example.com --subject "Report" --body "See attached" -A file1.pdf file2.xlsx

  # Dry run (test without sending)
  python send_email.py --to user@example.com --subject "Test" --body "Hello" --dry-run

  # Authenticate first
  python email_mcp_server.py --authenticate --credentials ../../credentials.json
'''
    )
    
    parser.add_argument('--to', '-t', required=True,
                       help='Recipient email address')
    parser.add_argument('--subject', '-s', required=True,
                       help='Email subject')
    parser.add_argument('--body', '-b', required=True,
                       help='Email body text')
    parser.add_argument('--attachments', '-A', nargs='+',
                       help='Attachment file paths')
    parser.add_argument('--credentials', '-c',
                       help='Path to OAuth credentials JSON')
    parser.add_argument('--token', help='Path to token file')
    parser.add_argument('--dry-run', action='store_true',
                       help='Log but don\'t send')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Minimal output')
    
    args = parser.parse_args()
    
    result = send_email(
        to=args.to,
        subject=args.subject,
        body=args.body,
        attachments=args.attachments,
        credentials_path=args.credentials,
        token_path=args.token,
        dry_run=args.dry_run
    )
    
    # Exit with appropriate code
    if result.get('status') in ['sent', 'dry_run']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
