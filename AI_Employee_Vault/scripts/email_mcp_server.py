#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email MCP Server - Send emails via Gmail API.

Implements Model Context Protocol (MCP) for email operations.
Supports sending, drafting, searching, and replying to emails.

Usage:
    python email_mcp_server.py [--port PORT]
    python email_mcp_server.py --authenticate
"""

import sys
import json
import base64
import pickle
import argparse
import logging
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, Dict, Any, List

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Missing dependencies. Install with:")
    print("  pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('email-mcp-server')

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.compose']


class EmailMCPServer:
    """MCP Server for Gmail operations."""
    
    def __init__(self, credentials_path: str, token_path: str, 
                 sender_name: str = "", sender_email: str = "",
                 dry_run: bool = False):
        """
        Initialize Email MCP Server.
        
        Args:
            credentials_path: Path to OAuth credentials JSON
            token_path: Path to save/load auth token
            sender_name: Name to use in From field
            sender_email: Email address to send from
            dry_run: If True, log emails but don't send
        """
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.dry_run = dry_run
        self.service: Optional[build] = None
    
    def authenticate(self) -> bool:
        """Run OAuth authentication flow."""
        if not self.credentials_path.exists():
            logger.error(f"Credentials file not found: {self.credentials_path}")
            return False
        
        try:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_path, scopes=SCOPES
            )
            creds = flow.run_local_server(port=0)
            
            # Save token
            self.token_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.token_path, 'wb') as f:
                pickle.dump(creds, f)
            
            logger.info("Authentication successful!")
            return True
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def get_service(self) -> Optional[build]:
        """Get authenticated Gmail API service."""
        if not self.token_path.exists():
            logger.error("Token not found. Run with --authenticate first.")
            return None
        
        try:
            creds = pickle.loads(self.token_path.read_bytes())
            
            if not creds.valid:
                if creds.expired and creds.refresh_token:
                    creds.refresh(None)
                    with open(self.token_path, 'wb') as f:
                        pickle.dump(creds, f)
                else:
                    logger.error("Credentials invalid. Re-authenticate.")
                    return None
            
            return build('gmail', 'v1', credentials=creds)
            
        except Exception as e:
            logger.error(f"Error getting service: {e}")
            return None
    
    def send_email(self, to: str, subject: str, body: str,
                   cc: List[str] = None, bcc: List[str] = None,
                   attachments: List[str] = None, 
                   is_html: bool = False) -> Dict[str, Any]:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body (plain text or HTML)
            cc: CC recipients
            bcc: BCC recipients
            attachments: File paths to attach
            is_html: If True, body is HTML
            
        Returns:
            Dict with 'id' and 'thread_id' of sent message
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would send email to {to}")
            logger.info(f"[DRY RUN] Subject: {subject}")
            return {'id': 'dry_run', 'thread_id': 'dry_run', 'dry_run': True}
        
        if not self.service:
            self.service = self.get_service()
        
        if not self.service:
            raise Exception("Gmail service not available")
        
        # Create message
        message = MIMEMultipart() if attachments else MIMEMultipart('alternative')
        message['to'] = ', '.join([to] + (cc or []))
        message['subject'] = subject
        
        if self.sender_name and self.sender_email:
            message['from'] = f"{self.sender_name} <{self.sender_email}>"
        elif self.sender_email:
            message['from'] = self.sender_email
        
        # Add body
        if is_html:
            message.attach(MIMEText(body, 'html'))
        else:
            message.attach(MIMEText(body, 'plain'))
        
        # Add attachments
        if attachments:
            for path in attachments:
                try:
                    with open(path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    filename = Path(path).name
                    part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
                    message.attach(part)
                    logger.info(f"Attached: {filename}")
                except Exception as e:
                    logger.warning(f"Failed to attach {path}: {e}")
        
        # Encode and send
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        try:
            result = self.service.users().messages().send(
                userId='me', body={'raw': raw}
            ).execute()
            
            logger.info(f"Email sent to {to}, ID: {result['id']}")
            
            return {
                'id': result['id'],
                'thread_id': result.get('threadId', ''),
                'status': 'sent'
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise Exception(f"Failed to send email: {e}")
    
    def create_draft(self, to: str, subject: str, body: str,
                     cc: List[str] = None, attachments: List[str] = None,
                     is_html: bool = False) -> Dict[str, Any]:
        """
        Create a draft email.
        
        Returns:
            Dict with 'draft_id' and 'message_id'
        """
        if not self.service:
            self.service = self.get_service()
        
        # Create message (same as send_email)
        message = MIMEMultipart() if attachments else MIMEMultipart('alternative')
        message['to'] = ', '.join([to] + (cc or []))
        message['subject'] = subject
        
        if self.sender_name and self.sender_email:
            message['from'] = f"{self.sender_name} <{self.sender_email}>"
        
        message.attach(MIMEText(body, 'html' if is_html else 'plain'))
        
        if attachments:
            for path in attachments:
                with open(path, 'rb') as f:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{Path(path).name}"')
                message.attach(part)
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        try:
            draft = self.service.users().drafts().create(
                userId='me', body={'message': {'raw': raw}}
            ).execute()
            
            logger.info(f"Draft created: {draft['id']}")
            
            return {
                'draft_id': draft['id'],
                'message_id': draft['message']['id'],
                'status': 'draft'
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise Exception(f"Failed to create draft: {e}")
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search emails in Gmail.
        
        Args:
            query: Gmail search query
            max_results: Maximum results to return
            
        Returns:
            List of email metadata
        """
        if not self.service:
            self.service = self.get_service()
        
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                detail = self.service.users().messages().get(
                    userId='me', id=msg['id'], format='metadata',
                    metadataHeaders=['from', 'to', 'subject', 'date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in detail['payload']['headers']}
                emails.append({
                    'id': msg['id'],
                    'thread_id': detail['threadId'],
                    'from': headers.get('From', ''),
                    'to': headers.get('To', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': detail.get('snippet', '')
                })
            
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            return []
    
    def reply_to_email(self, message_id: str, body: str,
                       include_original: bool = True) -> Dict[str, Any]:
        """
        Reply to an existing email.
        
        Args:
            message_id: Original message ID
            body: Reply body
            include_original: Include original message
            
        Returns:
            Dict with 'id' and 'thread_id' of reply
        """
        if not self.service:
            self.service = self.get_service()
        
        # Get original message to extract thread and headers
        original = self.service.users().messages().get(
            userId='me', id=message_id
        ).execute()
        
        headers = {h['name']: h['value'] for h in original['payload']['headers']}
        
        # Create reply
        message = MIMEMultipart()
        message['to'] = headers.get('From', '')
        message['subject'] = f"Re: {headers.get('Subject', '')}"
        message['in-reply-to'] = message_id
        message['references'] = message_id
        
        if self.sender_name and self.sender_email:
            message['from'] = f"{self.sender_name} <{self.sender_email}>"
        
        # Add body
        reply_body = body
        if include_original:
            reply_body += f"\n\n--- Original Message ---\n\n{original.get('snippet', '')}"
        
        message.attach(MIMEText(reply_body, 'plain'))
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        try:
            result = self.service.users().messages().send(
                userId='me', body={'raw': raw}
            ).execute()
            
            logger.info(f"Reply sent, ID: {result['id']}")
            
            return {
                'id': result['id'],
                'thread_id': result.get('threadId', ''),
                'status': 'sent'
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            raise Exception(f"Failed to send reply: {e}")


# MCP Protocol Handlers

def handle_tool_call(server: EmailMCPServer, tool_name: str, arguments: Dict) -> Dict:
    """Handle MCP tool call."""
    
    tools = {
        'email_send': lambda: server.send_email(**arguments),
        'email_draft': lambda: server.create_draft(**arguments),
        'email_search': lambda: server.search_emails(**arguments),
        'email_reply': lambda: server.reply_to_email(**arguments),
    }
    
    if tool_name not in tools:
        return {'error': f'Unknown tool: {tool_name}'}
    
    try:
        result = tools[tool_name]()
        return {'result': result}
    except Exception as e:
        return {'error': str(e)}


def main():
    """Main entry point - simple MCP server implementation."""
    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--port', '-p', type=int, default=8809,
                       help='Server port (default: 8809)')
    parser.add_argument('--credentials', '-c',
                       help='Path to OAuth credentials JSON')
    parser.add_argument('--token', '-t',
                       help='Path to token file')
    parser.add_argument('--authenticate', '-a', action='store_true',
                       help='Run authentication flow')
    parser.add_argument('--dry-run', action='store_true',
                       help='Log emails but don\'t send')
    parser.add_argument('--sender-name', help='Sender name')
    parser.add_argument('--sender-email', help='Sender email')
    
    # New: Direct send options
    parser.add_argument('--send', action='store_true',
                       help='Send email directly')
    parser.add_argument('--to', help='Recipient email address')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--attachments', '-A', nargs='+',
                       help='Attachment file paths')
    
    args = parser.parse_args()
    
    # Default paths
    credentials_path = Path(args.credentials) if args.credentials else Path.cwd().parent.parent / 'credentials.json'
    token_path = Path(args.token) if args.token else Path.home() / '.email_token.pkl'
    
    # Create server
    server = EmailMCPServer(
        str(credentials_path),
        str(token_path),
        sender_name=args.sender_name,
        sender_email=args.sender_email,
        dry_run=args.dry_run
    )
    
    if args.authenticate:
        if server.authenticate():
            print("Authentication successful!")
        else:
            print("Authentication failed")
            sys.exit(1)
    
    elif args.send:
        # Direct send mode
        if not args.to or not args.subject:
            print("Error: --to and --subject are required for sending")
            sys.exit(1)
        
        print(f"Sending email to {args.to}...")
        result = server.send_email(
            to=args.to,
            subject=args.subject,
            body=args.body or '',
            attachments=args.attachments
        )
        
        if result.get('status') == 'sent' or result.get('dry_run'):
            print(f"Email sent! ID: {result.get('id')}")
        else:
            print(f"Failed: {result}")
    
    else:
        # Simple interactive mode for testing
        print(f"Email MCP Server (dry_run={args.dry_run})")
        print("Use MCP client to call tools:")
        print("  - email_send")
        print("  - email_draft")
        print("  - email_search")
        print("  - email_reply")
        print("\nOr use --send flag for direct sending:")
        print("  python email_mcp_server.py --send --to email@example.com --subject 'Hello' --body 'Message'")


if __name__ == '__main__':
    main()
