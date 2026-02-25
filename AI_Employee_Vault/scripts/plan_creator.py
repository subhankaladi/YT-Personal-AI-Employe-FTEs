#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan Creator - Automatically creates Plan.md and Approval files from action files.

This bypasses the need for Qwen Code to create files - it just analyzes and creates.
"""

import sys
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('plan_creator')


class PlanCreator:
    """Automatically create plans and approval requests from action files."""
    
    def __init__(self, vault_path: Path):
        self.vault = vault_path
        self.needs_action = vault_path / 'Needs_Action'
        self.plans = vault_path / 'Plans'
        self.pending_approval = vault_path / 'Pending_Approval'
        self.done = vault_path / 'Done'
        self.handbook = vault_path / 'Company_Handbook.md'
        
        for folder in [self.plans, self.pending_approval, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def process_email(self, email_file: Path) -> Optional[Dict[str, Any]]:
        """
        Process an email action file and create plan + approval if needed.
        
        Returns:
            Dict with plan_path and approval_path (if created)
        """
        content = email_file.read_text()
        
        # Extract email details
        email_data = self._parse_email_frontmatter(content)
        
        if not email_data:
            logger.warning(f"Could not parse email: {email_file.name}")
            return None
        
        # Determine if approval is needed
        needs_approval = self._check_approval_needed(email_data)
        
        # Create plan
        plan_path = self._create_plan(email_data, needs_approval)
        
        # Create approval if needed
        approval_path = None
        if needs_approval:
            approval_path = self._create_approval_request(email_data)
        
        return {
            'email_file': str(email_file),
            'plan_path': str(plan_path),
            'approval_path': str(approval_path) if approval_path else None,
            'needs_approval': needs_approval
        }
    
    def _parse_email_frontmatter(self, content: str) -> Optional[Dict[str, str]]:
        """Parse YAML frontmatter from email file."""
        data = {}
        
        # Extract from
        match = re.search(r'from:\s*(.+)', content)
        if match:
            data['from'] = match.group(1).strip()
        
        # Extract to
        match = re.search(r'to:\s*(.+)', content)
        if match:
            data['to'] = match.group(1).strip()
        
        # Extract subject
        match = re.search(r'subject:\s*(.+)', content)
        if match:
            data['subject'] = match.group(1).strip()
        
        # Extract received
        match = re.search(r'received:\s*(.+)', content)
        if match:
            data['received'] = match.group(1).strip()
        
        # Extract priority
        match = re.search(r'priority:\s*(.+)', content)
        if match:
            data['priority'] = match.group(1).strip()
        
        # Extract message_id
        match = re.search(r'message_id:\s*(.+)', content)
        if match:
            data['message_id'] = match.group(1).strip()
        
        # Extract email body (after frontmatter)
        body_match = re.search(r'# Email Content\s*\n(.*?)(?:^---|\n# |\Z)', content, re.DOTALL | re.MULTILINE)
        if body_match:
            data['body'] = body_match.group(1).strip()
        
        return data if data else None
    
    def _check_approval_needed(self, email_data: Dict[str, str]) -> bool:
        """Check if this email requires approval to reply."""
        # Check if sending to new contact (not in known contacts)
        known_contacts = ['@yourcompany.com', '@yourdomain.com']  # Add your domains
        
        to_email = email_data.get('to', '')
        from_email = email_data.get('from', '')
        
        # If replying to external email, require approval
        if to_email and not any(domain in to_email for domain in known_contacts):
            return True
        
        # If email contains attachments, require approval
        if 'attachments' in str(email_data):
            return True
        
        # If high priority or contains sensitive keywords
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()
        
        sensitive_keywords = ['payment', 'invoice', 'contract', 'legal', 'money', 'bank']
        if any(kw in subject or kw in body for kw in sensitive_keywords):
            return True
        
        return False
    
    def _create_plan(self, email_data: Dict[str, str], needs_approval: bool) -> Path:
        """Create Plan.md file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_id = email_data.get('message_id', timestamp)[:8]
        filename = f'PLAN_email_{plan_id}.md'
        
        plan_content = f'''---
created: {datetime.now().isoformat()}
status: in_progress
objective: Process email and send reply
related_to: EMAIL_{plan_id}.md
approval_required: {str(needs_approval).lower()}
---

# Plan: Process Email - {email_data.get('subject', 'No Subject')}

## Objective
Process incoming email and send appropriate reply.

## Email Details

| Field | Value |
|-------|-------|
| From | {email_data.get('from', 'Unknown')} |
| To | {email_data.get('to', 'N/A')} |
| Subject | {email_data.get('subject', 'No Subject')} |
| Received | {email_data.get('received', 'Unknown')} |
| Priority | {email_data.get('priority', 'normal')} |

## Steps

- [x] **Step 1: Read and analyze email**
  - Email received and parsed
  - Priority determined: {email_data.get('priority', 'normal')}

- [ ] **Step 2: Draft reply**
  - Compose appropriate response
  - Review for tone and accuracy

- [ ] **Step 3: {"Request approval" if needs_approval else "Send email"}**
  {"- Approval request created in /Pending_Approval/" if needs_approval else "- Send reply via Email MCP"}

- [ ] **Step 4: Log and archive**
  - Log action in /Logs/
  - Move email to /Done/

## Notes

Auto-generated plan by Plan Creator v0.1

---
*Generated automatically by AI Employee Plan Creator*
'''
        
        plan_path = self.plans / filename
        plan_path.write_text(plan_content)
        logger.info(f"Created plan: {filename}")
        
        return plan_path
    
    def _create_approval_request(self, email_data: Dict[str, str]) -> Path:
        """Create approval request file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plan_id = email_data.get('message_id', timestamp)[:8]
        filename = f'APPROVAL_email_reply_{plan_id}.md'
        
        # Generate suggested reply
        suggested_reply = self._generate_suggested_reply(email_data)
        
        approval_content = f'''---
type: approval_request
action: email_send
to: {email_data.get('from', '').split('<')[-1].strip('>').strip()}
subject: Re: {email_data.get('subject', 'No Subject')}
created: {datetime.now().isoformat()}
expires: {(datetime.now().replace(hour=23, minute=59)).isoformat()}
status: pending
priority: {email_data.get('priority', 'normal')}
---

# Approval Required: Send Email Reply

## Email Details

| Field | Value |
|-------|-------|
| To | {email_data.get('from', 'Unknown')} |
| Subject | Re: {email_data.get('subject', 'No Subject')} |
| Original Priority | {email_data.get('priority', 'normal')} |

## Suggested Reply

{suggested_reply}

## Why Approval Required

This email requires human approval before sending because:
- Replying to external contact
- Ensure response is appropriate and accurate

---

## To Approve

Move this file to `/Approved` folder.

## To Reject

Move this file to `/Rejected` folder and add a comment.

---
*Generated automatically by AI Employee Plan Creator*
'''
        
        approval_path = self.pending_approval / filename
        approval_path.write_text(approval_content)
        logger.info(f"Created approval request: {filename}")
        
        return approval_path
    
    def _generate_suggested_reply(self, email_data: Dict[str, str]) -> str:
        """Generate a suggested reply based on email content."""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '')
        
        # Check for common patterns
        if 'greeting' in subject or 'how are you' in body.lower():
            return f'''Hi,

Thank you for your message! I'm doing well, thank you.

Hope you're doing great too.

Best regards'''
        
        elif 'invoice' in subject or 'payment' in subject:
            return f'''Dear Valued Client,

Thank you for your inquiry regarding the invoice.

I will process your request and send the invoice shortly.

Best regards'''
        
        elif 'urgent' in subject or 'asap' in body.lower():
            return f'''Dear Sender,

I received your urgent message and will respond as soon as possible.

Thank you for your patience.

Best regards'''
        
        else:
            return f'''Dear Sender,

Thank you for your email. I have received your message and will respond shortly.

Best regards'''


def main():
    """Process all email files in Needs_Action."""
    if len(sys.argv) < 2:
        print("Usage: python plan_creator.py /path/to/vault")
        sys.exit(1)
    
    vault_path = Path(sys.argv[1])
    if not vault_path.exists():
        print(f"Vault not found: {vault_path}")
        sys.exit(1)
    
    creator = PlanCreator(vault_path)
    
    # Find all email files
    email_files = list(creator.needs_action.glob('EMAIL_*.md'))
    
    if not email_files:
        print("No email files found in Needs_Action/")
        return
    
    print(f"Found {len(email_files)} email(s) to process")
    
    for email_file in email_files:
        print(f"\nProcessing: {email_file.name}")
        result = creator.process_email(email_file)
        
        if result:
            print(f"  Plan created: {result['plan_path']}")
            if result['approval_path']:
                print(f"  Approval created: {result['approval_path']}")
            else:
                print("  No approval needed")


if __name__ == '__main__':
    main()
