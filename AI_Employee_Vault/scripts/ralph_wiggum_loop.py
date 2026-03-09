# Ralph Wiggum Loop Implementation - Gold Tier
# Persistence pattern for multi-step autonomous task completion

import time
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
import subprocess
import sys

logger = logging.getLogger("ralph_wiggum")

class RalphWiggumLoop:
    """
    Ralph Wiggum Loop - Keeps Claude Code iterating until task is complete.
    
    This implements the "Stop hook" pattern where:
    1. Claude works on a task
    2. Claude tries to exit
    3. Stop hook checks: Is task complete?
    4. YES → Allow exit
    5. NO → Block exit, re-inject prompt (loop continues)
    """
    
    def __init__(
        self,
        vault_path: str,
        task_file: str = None,
        max_iterations: int = 10,
        completion_signal: str = "TASK_COMPLETE",
        done_folder: str = "Done"
    ):
        self.vault_path = Path(vault_path)
        self.done_folder = self.vault_path / done_folder
        self.plans_folder = self.vault_path / "Plans"
        self.pending_folder = self.vault_path / "Pending_Approval"
        self.approved_folder = self.vault_path / "Approved"
        self.logs_folder = self.vault_path / "Logs"
        
        self.task_file = task_file
        self.max_iterations = max_iterations
        self.completion_signal = completion_signal
        self.current_iteration = 0
        self.task_start_time = None
        
        # Ensure folders exist
        for folder in [self.done_folder, self.plans_folder, self.logs_folder]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def is_task_complete(self, task_id: str) -> bool:
        """Check if task is complete by looking for completion signal"""
        
        # Method 1: Check if task file moved to Done folder
        done_file = self.done_folder / f"{task_id}.md"
        if done_file.exists():
            logger.info(f"Task complete: {task_id} found in Done folder")
            return True
        
        # Method 2: Check for completion signal in task file content
        if self.task_file:
            task_path = self.plans_folder / self.task_file
            if task_path.exists():
                content = task_path.read_text()
                if f"<{self.completion_signal}>" in content or f"</{self.completion_signal}>" in content:
                    logger.info(f"Task complete: {task_id} has completion signal")
                    return True
        
        # Method 3: Check if all plan items are checked off
        if self.task_file:
            task_path = self.plans_folder / self.task_file
            if task_path.exists():
                content = task_path.read_text()
                lines = content.split('\n')
                unchecked = [l for l in lines if l.strip().startswith('- [ ]')]
                
                if len(unchecked) == 0:
                    logger.info(f"Task complete: All plan items checked for {task_id}")
                    return True
        
        return False
    
    def get_pending_approvals(self) -> List[Path]:
        """Get list of pending approval files"""
        if not self.pending_folder.exists():
            return []
        return list(self.pending_folder.glob("*.md"))
    
    def wait_for_approval(self, timeout_hours: int = 24) -> bool:
        """Wait for human to approve pending items"""
        pending = self.get_pending_approvals()
        
        if not pending:
            return True
        
        logger.info(f"Waiting for {len(pending)} approval(s)...")
        
        start_time = time.time()
        timeout_seconds = timeout_hours * 3600
        
        while time.time() - start_time < timeout_seconds:
            pending = self.get_pending_approvals()
            
            if not pending:
                logger.info("All approvals received!")
                return True
            
            # Check if any approvals moved to approved folder
            approved = list(self.approved_folder.glob("*.md"))
            if approved:
                logger.info(f"Received {len(approved)} approval(s)")
            
            time.sleep(30)  # Check every 30 seconds
        
        logger.warning("Approval timeout!")
        return False
    
    def create_task_state(self, task_id: str, prompt: str) -> Path:
        """Create task state file"""
        state = {
            "task_id": task_id,
            "prompt": prompt,
            "created": datetime.now().isoformat(),
            "iteration": 0,
            "status": "pending",
            "max_iterations": self.max_iterations
        }
        
        state_file = self.plans_folder / f"STATE_{task_id}.json"
        state_file.write_text(json.dumps(state, indent=2))
        
        logger.info(f"Created task state: {state_file}")
        return state_file
    
    def update_task_state(self, task_id: str, **kwargs):
        """Update task state file"""
        state_file = self.plans_folder / f"STATE_{task_id}.json"
        
        if not state_file.exists():
            self.create_task_state(task_id, "")
        
        state = json.loads(state_file.read_text())
        state.update(kwargs)
        state["updated"] = datetime.now().isoformat()
        
        state_file.write_text(json.dumps(state, indent=2))
    
    def get_task_state(self, task_id: str) -> Optional[Dict]:
        """Get task state"""
        state_file = self.plans_folder / f"STATE_{task_id}.json"
        
        if not state_file.exists():
            return None
        
        return json.loads(state_file.read_text())
    
    def log_iteration(self, task_id: str, iteration: int, output: str):
        """Log iteration output"""
        log_file = self.logs_folder / f"ralph_{task_id}_iter_{iteration}.log"
        log_file.write_text(output)
        
        # Also append to main log
        main_log = self.logs_folder / f"ralph_{task_id}.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "iteration": iteration,
            "status": "completed" if self.is_task_complete(task_id) else "in_progress"
        }
        
        with open(main_log, "a") as f:
            f.write(json.dumps(entry) + "\n")
    
    def run_claude_iteration(
        self,
        prompt: str,
        task_id: str,
        iteration: int,
        previous_output: str = None
    ) -> str:
        """Run a single Claude iteration"""
        
        # Build the prompt
        full_prompt = prompt
        
        if previous_output:
            full_prompt += f"\n\n[Previous iteration output:]\n{previous_output}\n\nContinue working on this task."
        
        # Run Claude Code
        try:
            result = subprocess.run(
                ["claude", "--prompt", full_prompt],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per iteration
                cwd=str(self.vault_path)
            )
            
            output = result.stdout + result.stderr
            self.log_iteration(task_id, iteration, output)
            
            return output
            
        except subprocess.TimeoutExpired:
            logger.error(f"Iteration {iteration} timed out")
            return "ERROR: Iteration timed out"
        except Exception as e:
            logger.error(f"Iteration {iteration} error: {e}")
            return f"ERROR: {str(e)}"
    
    def run(
        self,
        prompt: str,
        task_id: str = None,
        wait_for_approval: bool = True,
        approval_timeout: int = 24
    ) -> bool:
        """
        Run the Ralph Wiggum loop until task is complete.
        
        Args:
            prompt: The task prompt for Claude
            task_id: Unique task identifier (auto-generated if not provided)
            wait_for_approval: Whether to wait for human approval
            approval_timeout: Timeout for approval in hours
        
        Returns:
            True if task completed successfully, False otherwise
        """
        
        if not task_id:
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.task_start_time = datetime.now()
        self.current_iteration = 0
        
        logger.info(f"Starting Ralph Wiggum Loop for task: {task_id}")
        logger.info(f"Max iterations: {self.max_iterations}")
        
        # Create initial task state
        self.create_task_state(task_id, prompt)
        
        previous_output = None
        
        while self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            
            logger.info(f"=== Iteration {self.current_iteration}/{self.max_iterations} ===")
            
            # Run Claude iteration
            output = self.run_claude_iteration(
                prompt=prompt,
                task_id=task_id,
                iteration=self.current_iteration,
                previous_output=previous_output
            )
            
            # Check if task is complete
            if self.is_task_complete(task_id):
                logger.info(f"✓ Task {task_id} completed in {self.current_iteration} iterations")
                self.update_task_state(task_id, status="completed")
                return True
            
            # Check for pending approvals
            if wait_for_approval:
                pending = self.get_pending_approvals()
                if pending:
                    logger.info(f"Waiting for {len(pending)} approval(s)...")
                    
                    if not self.wait_for_approval(timeout_hours=approval_timeout):
                        logger.error("Approval timeout or rejected")
                        self.update_task_state(task_id, status="approval_failed")
                        return False
                    
                    logger.info("Approvals received, continuing...")
            
            previous_output = output
            self.update_task_state(task_id, iteration=self.current_iteration)
        
        # Max iterations reached
        logger.error(f"✗ Task {task_id} did not complete in {self.max_iterations} iterations")
        self.update_task_state(task_id, status="max_iterations_reached")
        return False


class GoldTierOrchestrator:
    """
    Gold Tier Orchestrator - Coordinates all watchers and Ralph Wiggum loop
    """
    
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.in_progress = self.vault_path / "In_Progress"
        self.done = self.vault_path / "Done"
        self.plans = self.vault_path / "Plans"
        self.logs = self.vault_path / "Logs"
        
        # Ensure folders exist
        for folder in [self.needs_action, self.in_progress, self.done, self.plans, self.logs]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.ralph = RalphWiggumLoop(str(vault_path))
        self.processed_files = set()
    
    def claim_task(self, file: Path, agent_name: str = "gold_tier") -> bool:
        """Claim a task by moving to In_Progress (prevents double-work)"""
        try:
            agent_folder = self.in_progress / agent_name
            agent_folder.mkdir(parents=True, exist_ok=True)
            
            dest = agent_folder / file.name
            file.rename(dest)
            logger.info(f"Claimed task: {file.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to claim task: {e}")
            return False
    
    def complete_task(self, file: Path, agent_name: str = "gold_tier"):
        """Move task to Done folder"""
        try:
            source = self.in_progress / agent_name / file.name
            if source.exists():
                dest = self.done / file.name
                source.rename(dest)
                logger.info(f"Completed task: {file.name}")
        except Exception as e:
            logger.error(f"Failed to complete task: {e}")
    
    def process_needs_action(self, use_ralph: bool = True):
        """Process all files in Needs_Action folder"""
        files = list(self.needs_action.glob("*.md"))
        
        if not files:
            logger.debug("No files in Needs_Action")
            return
        
        logger.info(f"Found {len(files)} files to process")
        
        for file in files:
            if file.name in self.processed_files:
                continue
            
            # Claim the task
            if not self.claim_task(file):
                continue
            
            self.processed_files.add(file.name)
            
            if use_ralph:
                # Use Ralph Wiggum loop for complex tasks
                prompt = f"""Process this action file: {file.name}

1. Read and understand the request
2. Create a plan in /Plans if multi-step
3. Execute the plan step by step
4. Request approval for sensitive actions
5. Move to /Done when complete

Action file is in: {self.in_progress / 'gold_tier' / file.name}
"""
                success = self.ralph.run(
                    prompt=prompt,
                    task_id=file.stem,
                    wait_for_approval=True
                )
            else:
                # Simple processing without Ralph loop
                logger.info(f"Processing {file.name} (simple mode)")
                # Simple processing logic here
            
            # Mark as complete
            self.complete_task(file)
    
    def run_continuous(self, check_interval: int = 30):
        """Run orchestrator in continuous mode"""
        logger.info("Starting Gold Tier Orchestrator (continuous mode)")
        logger.info(f"Vault: {self.vault_path}")
        logger.info(f"Check interval: {check_interval}s")
        
        try:
            while True:
                self.process_needs_action(use_ralph=True)
                time.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("Stopping Gold Tier Orchestrator")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ralph Wiggum Loop - Gold Tier")
    parser.add_argument("vault_path", type=str, help="Path to Obsidian vault")
    parser.add_argument("--prompt", type=str, help="Task prompt")
    parser.add_argument("--task-id", type=str, help="Task ID")
    parser.add_argument("--max-iterations", type=int, default=10, help="Max iterations")
    parser.add_argument("--no-approval-wait", action="store_true", help="Don't wait for approvals")
    parser.add_argument("--orchestrator", action="store_true", help="Run as orchestrator")
    parser.add_argument("--interval", type=int, default=30, help="Check interval (orchestrator)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.orchestrator:
        orchestrator = GoldTierOrchestrator(args.vault_path)
        orchestrator.run_continuous(check_interval=args.interval)
    else:
        ralph = RalphWiggumLoop(
            vault_path=args.vault_path,
            max_iterations=args.max_iterations
        )
        
        if args.prompt:
            success = ralph.run(
                prompt=args.prompt,
                task_id=args.task_id,
                wait_for_approval=not args.no_approval_wait
            )
            sys.exit(0 if success else 1)
        else:
            print("Provide --prompt or use --orchestrator mode")
            sys.exit(1)


if __name__ == "__main__":
    main()
