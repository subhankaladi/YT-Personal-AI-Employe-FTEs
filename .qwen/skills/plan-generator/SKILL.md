---
name: plan-generator
description: |
  Qwen Code reasoning loop that automatically creates Plan.md files for multi-step tasks.
  Analyzes action files in /Needs_Action, breaks down complex tasks into steps,
  identifies dependencies, and tracks progress. Supports approval checkpoints
  and automatic status updates.
---

# Plan Generator Skill

Automatically generate structured plans for multi-step tasks using Qwen Code.

## Overview

When Qwen Code encounters a complex task in `/Needs_Action`, it creates a `Plan.md` file that:
- Breaks down the task into actionable steps
- Identifies dependencies between steps
- Marks steps requiring human approval
- Tracks progress as work completes

## Plan Template

```markdown
---
created: 2026-02-24T10:30:00Z
status: in_progress
objective: Process invoice request and send to client
related_to: EMAIL_18d4f2a3b5c6e7f8.md
estimated_steps: 5
approval_required: true
---

# Plan: [Task Objective]

## Objective
Clear statement of what needs to be accomplished.

## Steps

- [x] **Step 1**: Completed action
  - Details about what was done
  - Result: success

- [ ] **Step 2**: Current action
  - What needs to be done
  - Dependencies: Step 1

- [ ] **Step 3**: Action requiring approval
  - **REQUIRES APPROVAL**
  - See: `/Pending_Approval/APPROVAL_*.md`

- [ ] **Step 4**: Conditional action
  - Only if Step 3 approved

- [ ] **Step 5**: Final action
  - Move to /Done when complete

## Notes
Additional context, decisions made, relevant information.

## Approval Required
Description of what needs human approval and why.

## Progress
- Completed: 1/5
- Pending: 3/5
- Awaiting Approval: 1/5
```

## How It Works

### 1. Qwen Code Analyzes Action File

```
qwen "Read EMAIL_*.md in Needs_Action. Determine if this is a multi-step task.
If yes, create a Plan.md with all required steps."
```

### 2. Plan Created in `/Plans/`

File named `PLAN_[task]_[timestamp].md`

### 3. Steps Executed Sequentially

- Complete steps that don't require approval
- Create approval requests for sensitive steps
- Wait for human approval
- Continue after approval

### 4. Progress Tracked in Plan

Checkboxes updated as work progresses

## Usage with Qwen Code

### Create Plan

```bash
cd AI_Employee_Vault
qwen "Create a plan for processing the email in Needs_Action folder"
```

### Execute Plan

```bash
qwen "Execute the next step in PLAN_*.md. Update the plan after completion."
```

### Check Progress

```bash
qwen "What's the status of all plans in the Plans folder?"
```

## Integration with Orchestrator

Add plan generation to orchestrator:

```python
def process_needs_action(self):
    pending = self.get_pending_items()
    
    for item in pending:
        # Check if this needs a plan (multi-step task)
        if self.is_complex_task(item):
            prompt = f"""Read {item.name}. This appears to be a multi-step task.
            
            Please:
            1. Analyze the task requirements
            2. Create a Plan.md in /Plans with all steps
            3. Identify which steps need approval
            4. Execute any steps that don't need approval
            """
            self.trigger_qwen(prompt)
```

## Example: Invoice Processing Plan

```markdown
---
created: 2026-02-24T10:30:00Z
status: in_progress
objective: Generate and send invoice to Client A
related_to: EMAIL_invoice_request.md
---

# Plan: Send Invoice to Client A

## Objective
Generate invoice PDF and email to client for January consulting work.

## Steps

- [x] **Identify client details**
  - Client: Client A (client@example.com)
  - Rate: $150/hour from Business_Goals.md
  - Hours: 10 hours (verified from Done folder)

- [x] **Calculate amount**
  - 10 hours × $150 = $1,500

- [x] **Generate invoice PDF**
  - Invoice #: 001
  - Created: 2026-02-24
  - Saved to: /Invoices/2026-01_ClientA.pdf

- [ ] **Send email with invoice** ⚠️
  - **REQUIRES APPROVAL**
  - To: client@example.com
  - Subject: Invoice #001 - January 2026
  - Attachment: invoice.pdf
  - See: `/Pending_Approval/EMAIL_send_invoice.md`

- [ ] **Log transaction**
  - Update /Accounting/2026-02_Transactions.md
  - Record $1,500 income

- [ ] **Archive and complete**
  - Move email action to /Done
  - Update Dashboard.md

## Approval Required

Email send requires approval per Company_Handbook.md:
- New contact: Yes
- Contains attachment: Yes
- Amount: $1,500

Approval file: `/Pending_Approval/EMAIL_send_invoice.md`

## Progress
- Completed: 3/6
- Pending: 2/6
- Awaiting Approval: 1/6
```

## Best Practices

1. **One plan per task**: Don't combine unrelated tasks
2. **Clear objectives**: State what success looks like
3. **Atomic steps**: Each step should be independently actionable
4. **Mark approvals**: Clearly identify steps needing approval
5. **Update progress**: Keep checkboxes current
6. **Link related files**: Reference action files, approvals, outputs

## Status Values

| Status | Meaning |
|--------|---------|
| `draft` | Plan created, not started |
| `in_progress` | Work actively happening |
| `blocked` | Waiting on approval/dependency |
| `completed` | All steps done |
| `cancelled` | Task abandoned |

## Next Steps

After creating plans:
1. Execute steps automatically where possible
2. Create approval files for sensitive steps
3. Update plan after each step completes
4. Move to /Done when all steps complete
