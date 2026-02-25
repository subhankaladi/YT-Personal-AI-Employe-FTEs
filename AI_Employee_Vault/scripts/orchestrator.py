#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator - Master process for the AI Employee.

This script:
1. Monitors the Needs_Action folder for new items
2. Triggers Qwen Code to process pending items
3. Updates the Dashboard.md with current status
4. Manages the overall workflow

Usage:
    python orchestrator.py /path/to/vault

Or run in background:
    python orchestrator.py ./AI_Employee_Vault &
"""

import sys
import re
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class Orchestrator:
    """Main orchestrator for the AI Employee system."""
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault
            check_interval: Seconds between checks (default: 30)
        """
        self.vault_path = Path(vault_path)
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Folder paths
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.plans = self.vault_path / 'Plans'
        self.accounting = self.vault_path / 'Accounting'
        self.briefings = self.vault_path / 'Briefings'
        self.logs = self.vault_path / 'Logs'
        self.dashboard = self.vault_path / 'Dashboard.md'
        self.handbook = self.vault_path / 'Company_Handbook.md'
        
        # Ensure all folders exist
        for folder in [self.inbox, self.needs_action, self.done, 
                       self.pending_approval, self.approved, self.plans,
                       self.accounting, self.briefings, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Track processed files to avoid duplicates
        self.processed_files = set()
    
    def get_pending_items(self) -> List[Path]:
        """Get all .md files in Needs_Action folder that haven't been processed."""
        if not self.needs_action.exists():
            return []
        
        pending = []
        for f in self.needs_action.glob('*.md'):
            if f.name not in self.processed_files:
                pending.append(f)
        
        # Sort by modification time (oldest first)
        pending.sort(key=lambda x: x.stat().st_mtime)
        return pending
    
    def get_approved_items(self) -> List[Path]:
        """Get all items in Approved folder ready for action."""
        if not self.approved.exists():
            return []
        return list(self.approved.glob('*.md'))
    
    def count_items(self) -> Dict[str, int]:
        """Count items in each folder."""
        return {
            'needs_action': len(list(self.needs_action.glob('*.md'))),
            'pending_approval': len(list(self.pending_approval.glob('*.md'))),
            'approved': len(list(self.approved.glob('*.md'))),
            'done': len(list(self.done.glob('*.md'))),
            'plans': len(list(self.plans.glob('*.md'))),
        }
    
    def update_dashboard(self):
        """Update the Dashboard.md with current status."""
        counts = self.count_items()
        timestamp = datetime.now().isoformat()

        if self.dashboard.exists():
            content = self.dashboard.read_text()
            
            # Update last_updated in frontmatter
            content = re.sub(
                r'last_updated: .*\n',
                f'last_updated: {timestamp}\n',
                content
            )

            # Update pending items count
            if '| **Pending Items** |' in content:
                content = re.sub(
                    r'\| \*\*Pending Items\*\* \| \d+ \|',
                    f'| **Pending Items** | {counts["needs_action"]} |',
                    content
                )

            # Update awaiting approval
            if '| **Awaiting Approval** |' in content:
                content = re.sub(
                    r'\| \*\*Awaiting Approval\*\* \| \d+ \|',
                    f'| **Awaiting Approval** | {counts["pending_approval"]} |',
                    content
                )

            self.dashboard.write_text(content)
            self.logger.info('Dashboard updated')

    def trigger_qwen(self, prompt: str) -> bool:
        """
        Trigger Qwen Code to process items.

        Args:
            prompt: The prompt to give Qwen Code

        Returns:
            True if successful, False otherwise
        """
        try:
            # Build the qwen command
            # On Windows, use qwen.cmd and shell=True for proper PATH resolution
            import platform
            import os
            use_shell = platform.system() == 'Windows'
            cmd_name = 'qwen.cmd' if use_shell else 'qwen'
            
            # Save current directory
            original_cwd = os.getcwd()
            
            # Change to vault directory
            os.chdir(str(self.vault_path))
            
            # Build command string for shell execution
            # Qwen Code accepts positional prompt directly
            cmd_string = f'{cmd_name} "{prompt}"'

            self.logger.info(f'Triggering Qwen Code: {prompt[:50]}...')

            # Run qwen code (non-interactive mode)
            result = subprocess.run(
                cmd_string,
                shell=use_shell,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Restore original directory
            os.chdir(original_cwd)

            if result.returncode == 0:
                self.logger.info('Qwen Code completed successfully')
                return True
            else:
                self.logger.error(f'Qwen Code error: {result.stderr}')
                return False

        except subprocess.TimeoutExpired:
            self.logger.error('Qwen Code timed out')
            return False
        except FileNotFoundError:
            self.logger.error('Qwen Code not found. Make sure it is installed.')
            return False
        except Exception as e:
            self.logger.error(f'Error triggering Qwen Code: {e}')
            return False
    
    def process_needs_action(self):
        """Process all items in Needs_Action folder."""
        pending = self.get_pending_items()

        if not pending:
            return

        self.logger.info(f'Found {len(pending)} pending item(s)')

        # Build prompt for Qwen - more specific instructions
        files = ', '.join([f.name for f in pending])
        prompt = f"""I have {len(pending)} item(s) in /Needs_Action that need processing: {files}

Please follow this workflow:

1. READ each file in /Needs_Action
2. READ Company_Handbook.md for rules of engagement
3. CREATE a Plan.md file in /Plans/ for each item with:
   - Clear objective
   - Step-by-step checklist
   - Mark steps that require approval
4. For steps requiring approval, CREATE approval request in /Pending_Approval/
5. For simple actions without approval, EXECUTE them directly
6. MOVE completed items to /Done/
7. UPDATE Dashboard.md with results

Be specific and create actual files, not just suggestions."""

        if self.trigger_qwen(prompt):
            # Mark files as processed
            for f in pending:
                self.processed_files.add(f.name)

    def process_approved(self):
        """Process items that have been approved by human."""
        approved = self.get_approved_items()

        if not approved:
            return

        self.logger.info(f'Found {len(approved)} approved item(s) ready for action')

        for item in approved:
            self.logger.info(f'Processing: {item.name}')
            
            # Read the approved file
            content = item.read_text()
            
            # Extract action type
            action_type = self._extract_field(content, 'action')
            
            self.logger.info(f'Action type: {action_type}')
            
            if action_type == 'email_send':
                # Extract email details
                to_email = self._extract_field(content, 'to')
                subject = self._extract_field(content, 'subject')
                
                # Extract body from the approval file
                body = self._extract_email_body(content)
                
                if not to_email or not subject:
                    self.logger.error(f'Missing email details in {item.name}')
                    continue
                
                self.logger.info(f"Sending email to {to_email}")
                self.logger.info(f"Subject: {subject}")
                
                # Send email using send_email.py script
                result = self._send_email_via_script(to_email, subject, body)
                
                if result.get('status') == 'sent':
                    self.logger.info(f"✓ Email sent successfully!")
                    self.log_action('email_sent', f"To: {to_email}, Subject: {subject}")
                else:
                    self.logger.error(f"✗ Email send failed: {result}")
            else:
                self.logger.info(f'Unknown action type: {action_type}')
            
            # Move to Done after processing
            dest = self.done / item.name
            try:
                item.rename(dest)
                self.logger.info(f'Moved to Done: {dest.name}')
                self.processed_files.add(item.name)
            except Exception as e:
                self.logger.error(f'Error moving file: {e}')
    
    def _send_email_via_script(self, to: str, subject: str, body: str) -> dict:
        """Send email using send_email.py script."""
        import subprocess
        
        try:
            # Build command
            cmd = [
                'python',
                'send_email.py',
                '--to', to,
                '--subject', subject,
                '--body', body,
                '--quiet'
            ]
            
            self.logger.info(f"Running: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            self.logger.info(f"stdout: {result.stdout}")
            self.logger.info(f"stderr: {result.stderr}")
            
            if result.returncode == 0 and 'Email sent successfully' in result.stdout:
                return {'status': 'sent'}
            else:
                return {'status': 'error', 'error': result.stderr or 'Unknown error'}
                
        except subprocess.TimeoutExpired:
            return {'status': 'error', 'error': 'Timeout'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _extract_field(self, content: str, field: str, default: str = '') -> str:
        """Extract field from markdown content."""
        import re
        # Try frontmatter format first (field: value)
        match = re.search(rf'^{field}:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return default
    
    def _extract_email_body(self, content: str) -> str:
        """Extract email body from approval file."""
        import re
        
        # Look for body after various section headers
        patterns = [
            r'## Suggested Reply\s*\n(.*?)(?:^##|^---|\Z)',  # ## Suggested Reply
            r'## Reply Content\s*\n(.*?)(?:^##|^---|\Z)',     # ## Reply Content
            r'## Content\s*\n(.*?)(?:^##|^---|\Z)',           # ## Content
            r'## Email Body\s*\n(.*?)(?:^##|^---|\Z)',        # ## Email Body
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
            if match:
                body = match.group(1).strip()
                # Remove markdown formatting
                body = re.sub(r'^\s*\*\s*', '', body, flags=re.MULTILINE)
                return body
        
        # If no section found, return content after frontmatter
        lines = content.split('\n')
        in_body = False
        body_lines = []
        
        for line in lines:
            if line.strip() == '---' and not in_body:
                in_body = True
                continue
            if in_body and not line.startswith('---'):
                if line.startswith('#'):
                    continue  # Skip headers
                body_lines.append(line)
        
        return '\n'.join(body_lines).strip()
    
    def send_email_via_mcp(self, to: str, subject: str, body: str) -> dict:
        """Send email using Email MCP Server."""
        import subprocess
        
        try:
            # Call email_mcp_server.py directly
            cmd = [
                'python',
                'email_mcp_server.py',
                '--send',
                '--to', to,
                '--subject', subject,
                '--body', body
            ]
            
            result = subprocess.run(
                cmd,
                cwd=str(Path(__file__).parent),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                return {'status': 'sent', 'id': 'sent_via_mcp'}
            else:
                return {'status': 'error', 'error': result.stderr}
                
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def log_action(self, action_type: str, details: str, status: str = 'success'):
        """Log an action to the logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'actor': 'orchestrator',
            'details': details,
            'status': status
        }
        
        import json
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def run(self):
        """Main orchestration loop."""
        self.logger.info('=' * 50)
        self.logger.info('AI Employee Orchestrator starting')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')
        self.logger.info('=' * 50)
        
        while True:
            try:
                # Process pending items
                self.process_needs_action()
                
                # Process approved items
                self.process_approved()
                
                # Update dashboard
                self.update_dashboard()
                
            except Exception as e:
                self.logger.error(f'Error in orchestration loop: {e}')
                self.log_action('error', str(e), 'failed')
            
            # Wait for next check
            import time
            time.sleep(self.check_interval)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py /path/to/vault")
        print("\nExample:")
        print("  python orchestrator.py ./AI_Employee_Vault")
        print("\nOptions:")
        print("  --interval SECONDS  Check interval (default: 30)")
        sys.exit(1)
    
    vault_path = sys.argv[1]
    
    # Parse optional arguments
    interval = 30
    if '--interval' in sys.argv:
        try:
            idx = sys.argv.index('--interval')
            interval = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            pass
    
    if not Path(vault_path).exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    orchestrator = Orchestrator(vault_path, interval)
    orchestrator.run()


if __name__ == '__main__':
    main()
