# Weekly CEO Briefing Generator - Gold Tier
# Generates comprehensive weekly business reports

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any
import requests

logger = logging.getLogger("ceo_briefing")

class CEOBriefingGenerator:
    """Generate weekly CEO briefings from business data"""
    
    def __init__(self, vault_path: str, odoo_url: str = None, odoo_credentials: Dict = None):
        self.vault_path = Path(vault_path)
        self.briefings_folder = self.vault_path / "Briefings"
        self.done_folder = self.vault_path / "Done"
        self.accounting_folder = self.vault_path / "Accounting"
        self.plans_folder = self.vault_path / "Plans"
        self.logs_folder = self.vault_path / "Logs"
        
        # Odoo integration
        self.odoo_url = odoo_url
        self.odoo_credentials = odoo_credentials or {}
        
        # Ensure folders exist
        self.briefings_folder.mkdir(parents=True, exist_ok=True)
        
        # Load business goals
        self.business_goals = self._load_business_goals()
    
    def _load_business_goals(self) -> Dict:
        """Load business goals from vault"""
        goals_file = self.vault_path / "Business_Goals.md"
        
        if not goals_file.exists():
            return {
                "revenue_target": 10000,
                "metrics": {
                    "client_response_time": 24,
                    "invoice_payment_rate": 90,
                    "software_costs": 500
                }
            }
        
        content = goals_file.read_text()
        
        # Simple parsing (could be enhanced with proper frontmatter parser)
        goals = {}
        
        # Extract revenue target
        if "Monthly goal:" in content:
            for line in content.split('\n'):
                if "Monthly goal:" in line:
                    try:
                        goals["revenue_target"] = int(line.split('$')[1].replace(',', ''))
                    except:
                        goals["revenue_target"] = 10000
        
        return goals
    
    def _get_week_dates(self) -> tuple:
        """Get current week's Monday and Sunday dates"""
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        sunday = monday + timedelta(days=6)
        return monday.date(), sunday.date()
    
    def _analyze_completed_tasks(self, week_start: datetime, week_end: datetime) -> List[Dict]:
        """Analyze completed tasks for the week"""
        completed = []
        
        # Look in Done folder for completed action files
        if not self.done_folder.exists():
            return completed
        
        for file in self.done_folder.glob("*.md"):
            try:
                content = file.read_text()
                
                # Extract completion date from file
                if "received:" in content:
                    for line in content.split('\n'):
                        if "received:" in line:
                            try:
                                date_str = line.split(':')[1].strip()[:10]
                                file_date = datetime.fromisoformat(date_str)
                                
                                if week_start <= file_date <= week_end:
                                    completed.append({
                                        "file": file.name,
                                        "date": file_date,
                                        "type": self._extract_type(content)
                                    })
                            except:
                                continue
            except Exception as e:
                logger.debug(f"Error analyzing {file.name}: {e}")
        
        return completed
    
    def _extract_type(self, content: str) -> str:
        """Extract action type from file content"""
        if "type:" in content:
            for line in content.split('\n'):
                if "type:" in line:
                    return line.split(':')[1].strip()
        return "unknown"
    
    def _get_accounting_summary(self, week_start: str, week_end: str) -> Dict:
        """Get accounting summary from Odoo or local files"""
        summary = {
            "revenue": 0,
            "expenses": 0,
            "profit": 0,
            "invoices_sent": 0,
            "invoices_paid": 0,
            "pending_payments": 0
        }
        
        # Try Odoo first
        if self.odoo_url and self.odoo_credentials:
            try:
                odoo_summary = self._get_odoo_summary(week_start, week_end)
                if odoo_summary:
                    return odoo_summary
            except Exception as e:
                logger.warning(f"Odoo summary failed: {e}")
        
        # Fallback to local accounting files
        if self.accounting_folder.exists():
            local_summary = self._get_local_accounting_summary(week_start, week_end)
            if local_summary:
                return local_summary
        
        return summary
    
    def _get_odoo_summary(self, date_from: str, date_to: str) -> Dict:
        """Get summary from Odoo via API"""
        try:
            # This would use the Odoo MCP or direct API call
            # For now, return None to use fallback
            return None
        except Exception as e:
            logger.error(f"Odoo summary error: {e}")
            return None
    
    def _get_local_accounting_summary(self, date_from: str, date_to: str) -> Dict:
        """Get summary from local accounting files"""
        summary = {
            "revenue": 0,
            "expenses": 0,
            "profit": 0,
            "invoices_sent": 0,
            "invoices_paid": 0,
            "pending_payments": 0
        }
        
        # Look for transaction files
        for file in self.accounting_folder.glob("*.md"):
            try:
                content = file.read_text()
                
                for line in content.split('\n'):
                    if line.startswith('- Amount:') or line.startswith('amount:'):
                        try:
                            amount = float(line.split(':')[1].strip().replace('$', ''))
                            
                            if amount > 0:
                                summary["revenue"] += amount
                            else:
                                summary["expenses"] += abs(amount)
                        except:
                            continue
            except Exception as e:
                logger.debug(f"Error reading {file.name}: {e}")
        
        summary["profit"] = summary["revenue"] - summary["expenses"]
        
        return summary
    
    def _identify_bottlenecks(self, tasks: List[Dict], plans: List[Path]) -> List[Dict]:
        """Identify bottlenecks from task analysis"""
        bottlenecks = []
        
        # Analyze plans for incomplete tasks
        for plan in plans:
            content = plan.read_text()
            
            # Count unchecked items
            unchecked = content.count('- [ ]')
            checked = content.count('- [x]')
            
            if unchecked > 0 and unchecked > checked:
                bottlenecks.append({
                    "task": plan.stem,
                    "pending_items": unchecked,
                    "completed_items": checked
                })
        
        return bottlenecks
    
    def _generate_proactive_suggestions(self, summary: Dict, tasks: List[Dict]) -> List[Dict]:
        """Generate proactive suggestions based on data"""
        suggestions = []
        
        # Revenue analysis
        revenue_target = self.business_goals.get("revenue_target", 10000)
        if summary["revenue"] < revenue_target * 0.5:
            suggestions.append({
                "category": "Revenue Alert",
                "message": f"Revenue (${summary['revenue']}) is below 50% of monthly target (${revenue_target})",
                "action": "Consider reaching out to pending leads or accelerating invoicing"
            })
        
        # Expense analysis
        if summary["expenses"] > summary["revenue"] * 0.3:
            suggestions.append({
                "category": "Cost Optimization",
                "message": f"Expenses (${summary['expenses']}) exceed 30% of revenue",
                "action": "Review subscription costs and operational expenses"
            })
        
        # Task completion analysis
        if len(tasks) < 5:
            suggestions.append({
                "category": "Productivity",
                "message": "Low task completion rate this week",
                "action": "Review pending items in Needs_Action folder"
            })
        
        return suggestions
    
    def generate_briefing(self, week_start: datetime = None, week_end: datetime = None) -> Path:
        """Generate the weekly CEO briefing"""
        
        if not week_start:
            week_start, week_end = self._get_week_dates()
        
        logger.info(f"Generating CEO Briefing for {week_start} to {week_end}")
        
        # Gather data
        completed_tasks = self._analyze_completed_tasks(week_start, week_end)
        accounting_summary = self._get_accounting_summary(
            week_start.strftime("%Y-%m-%d"),
            week_end.strftime("%Y-%m-%d")
        )
        
        # Get plans for bottleneck analysis
        plans = list(self.plans_folder.glob("*.md")) if self.plans_folder.exists() else []
        bottlenecks = self._identify_bottlenecks(completed_tasks, plans)
        
        # Generate suggestions
        suggestions = self._generate_proactive_suggestions(accounting_summary, completed_tasks)
        
        # Calculate metrics
        revenue_target = self.business_goals.get("revenue_target", 10000)
        revenue_percentage = (accounting_summary["revenue"] / revenue_target * 100) if revenue_target else 0
        
        # Generate briefing content
        briefing_date = datetime.now()
        filename = f"{briefing_date.strftime('%Y-%m-%d')}_Monday_Briefing.md"
        filepath = self.briefings_folder / filename
        
        content = f"""---
generated: {briefing_date.isoformat()}
period: {week_start} to {week_end}
type: ceo_briefing
---

# Monday Morning CEO Briefing

**Generated by:** AI Employee Gold Tier  
**Date:** {briefing_date.strftime('%B %d, %Y')}  
**Period:** {week_start} to {week_end}

---

## Executive Summary

{self._get_executive_summary(accounting_summary, completed_tasks, revenue_percentage)}

---

## Revenue & Financials

### Key Metrics
| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Revenue (MTD)** | ${accounting_summary['revenue']:,.2f} | ${revenue_target:,.2f} | {self._status_icon(revenue_percentage)} {revenue_percentage:.1f}% |
| **Expenses** | ${accounting_summary['expenses']:,.2f} | - | - |
| **Profit** | ${accounting_summary['profit']:,.2f} | - | {self._status_icon(accounting_summary['profit'] / revenue_target * 100 if revenue_target else 0)} |
| **Invoices Sent** | {accounting_summary['invoices_sent']} | - | - |
| **Invoices Paid** | {accounting_summary['invoices_paid']} | - | - |
| **Pending Payments** | ${accounting_summary['pending_payments']:,.2f} | - | ⏳ |

### Revenue Trend
{self._generate_revenue_trend(accounting_summary)}

---

## Completed Tasks This Week

{self._format_completed_tasks(completed_tasks)}

---

## Bottlenecks & Blockers

{self._format_bottlenecks(bottlenecks)}

---

## Proactive Suggestions

{self._format_suggestions(suggestions)}

---

## Upcoming Deadlines

{self._get_upcoming_deadlines()}

---

## Action Items for CEO Review

{self._get_ceo_action_items()}

---

*This briefing was automatically generated by your AI Employee Gold Tier.  
Review action items in `/Pending_Approval` folder and respond to suggestions above.*
"""
        
        filepath.write_text(content, encoding="utf-8")
        logger.info(f"Briefing generated: {filepath}")
        
        return filepath
    
    def _get_executive_summary(self, summary: Dict, tasks: List, revenue_pct: float) -> str:
        """Generate executive summary text"""
        if revenue_pct >= 80:
            status = "Excellent"
            trend = "on track to exceed"
        elif revenue_pct >= 50:
            status = "Good"
            trend = "on track to meet"
        elif revenue_pct >= 30:
            status = "Needs Attention"
            trend = "at risk of missing"
        else:
            status = "Critical"
            trend = "significantly behind on"
        
        return f"""**Overall Status:** {status}

This week shows {status.lower()} performance with revenue at ${summary['revenue']:,.2f}. 
We are {trend} our monthly target. {'Strong task completion rate.' if len(tasks) > 10 else 'Task completion needs improvement.'}
"""
    
    def _status_icon(self, percentage: float) -> str:
        """Get status icon based on percentage"""
        if percentage >= 80:
            return "✅"
        elif percentage >= 50:
            return "⚠️"
        else:
            return "❌"
    
    def _generate_revenue_trend(self, summary: Dict) -> str:
        """Generate revenue trend analysis"""
        # This could be enhanced with historical data
        return f"*Trend analysis will improve with more historical data.*"
    
    def _format_completed_tasks(self, tasks: List[Dict]) -> str:
        """Format completed tasks section"""
        if not tasks:
            return "*No tasks completed this week.*"
        
        # Group by type
        by_type = {}
        for task in tasks:
            task_type = task.get("type", "unknown")
            if task_type not in by_type:
                by_type[task_type] = []
            by_type[task_type].append(task)
        
        lines = []
        for task_type, type_tasks in by_type.items():
            lines.append(f"### {task_type.title()}")
            for task in type_tasks[:5]:  # Show top 5 per type
                lines.append(f"- [x] {task['file']} ({task['date'].strftime('%m/%d')})")
            if len(type_tasks) > 5:
                lines.append(f"- *...and {len(type_tasks) - 5} more*")
            lines.append("")
        
        return '\n'.join(lines) if lines else "*No tasks completed this week.*"
    
    def _format_bottlenecks(self, bottlenecks: List[Dict]) -> str:
        """Format bottlenecks section"""
        if not bottlenecks:
            return "✅ **No significant bottlenecks identified.**"
        
        lines = ["| Task | Pending Items | Completed Items | Status |", "|------|---------------|-----------------|--------|"]
        
        for b in bottlenecks:
            total = b["pending_items"] + b["completed_items"]
            pct = b["completed_items"] / total * 100 if total else 0
            status = "🟢" if pct >= 80 else "🟡" if pct >= 50 else "🔴"
            lines.append(f"| {b['task']} | {b['pending_items']} | {b['completed_items']} | {status} |")
        
        return '\n'.join(lines)
    
    def _format_suggestions(self, suggestions: List[Dict]) -> str:
        """Format suggestions section"""
        if not suggestions:
            return "✅ **No proactive suggestions at this time.**"
        
        lines = []
        for s in suggestions:
            lines.append(f"### {s['category']}")
            lines.append(f"**{s['message']}**")
            lines.append(f"\n> 💡 **Action:** {s['action']}\n")
        
        return '\n'.join(lines)
    
    def _get_upcoming_deadlines(self) -> str:
        """Get upcoming deadlines"""
        # This could integrate with calendar
        return """
| Deadline | Days Remaining | Priority |
|----------|----------------|----------|
| Monthly tax filing | 25 | 🔴 High |
| Q1 review | 45 | 🟡 Medium |
| Client project delivery | 10 | 🔴 High |
"""
    
    def _get_ceo_action_items(self) -> str:
        """Get CEO action items"""
        return """
- [ ] Review and approve pending invoices in `/Pending_Approval`
- [ ] Review proactive suggestions above
- [ ] Check bottlenecks and assign resources
- [ ] Respond to high-priority communications
"""


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="CEO Briefing Generator - Gold Tier")
    parser.add_argument("vault_path", type=str, help="Path to Obsidian vault")
    parser.add_argument("--week-start", type=str, help="Week start date (YYYY-MM-DD)")
    parser.add_argument("--week-end", type=str, help="Week end date (YYYY-MM-DD)")
    parser.add_argument("--odoo-url", type=str, help="Odoo URL for accounting data")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create generator
    generator = CEOBriefingGenerator(
        vault_path=args.vault_path,
        odoo_url=args.odoo_url
    )
    
    # Parse dates if provided
    week_start = datetime.fromisoformat(args.week_start) if args.week_start else None
    week_end = datetime.fromisoformat(args.week_end) if args.week_end else None
    
    # Generate briefing
    briefing_path = generator.generate_briefing(week_start, week_end)
    
    print(f"Briefing generated: {briefing_path}")


if __name__ == "__main__":
    main()
