---
name: windows-task-scheduler
description: |
  Schedule AI Employee tasks using Windows Task Scheduler.
  Automate daily briefings, periodic watcher checks, approval processing,
  and regular maintenance tasks. Includes XML templates and PowerShell
  scripts for easy setup.
---

# Windows Task Scheduler Integration

Automate AI Employee tasks using Windows Task Scheduler.

## Overview

Windows Task Scheduler allows you to:
- Run watcher scripts continuously in background
- Schedule daily/weekly briefings
- Process approvals at regular intervals
- Clean up old files automatically
- Send periodic reports

## Prerequisites

- Windows 10/11
- Python 3.13+ in PATH
- Qwen Code installed
- Administrator privileges (for creating tasks)

## Task Types

### 1. Continuous Watchers

Run watcher scripts that monitor for changes:

| Watcher | Interval | Priority |
|---------|----------|----------|
| File System Watcher | Continuous | High |
| Gmail Watcher | Every 2 min | Medium |
| WhatsApp Watcher | Every 30 sec | High |
| Orchestrator | Every 30 sec | High |

### 2. Scheduled Tasks

| Task | Frequency | Time |
|------|-----------|------|
| Daily Briefing | Daily | 8:00 AM |
| Process Approvals | Every hour | - |
| Weekly Audit | Weekly | Sunday 8 PM |
| Cleanup Old Files | Weekly | Sunday 11 PM |

## Setup: Continuous Watcher Task

### Step 1: Create Batch File

Create `start_watchers.bat` in `AI_Employee_Vault\scripts\`:

```batch
@echo off
cd /d "%~dp0"

REM Start File System Watcher
start "FS Watcher" python filesystem_watcher.py ..\

REM Start Orchestrator
start "Orchestrator" python orchestrator.py ..\ --interval 30

REM Start Approval Manager
start "Approval Manager" python approval_manager.py ..\ --check-every 30

echo All watchers started.
```

### Step 2: Create Scheduled Task

**Option A: Using Task Scheduler GUI**

1. Open Task Scheduler (`taskschd.msc`)
2. Click **Create Task** (not Basic Task - we need more options)
3. **General Tab:**
   - Name: `AI Employee - Watchers`
   - Description: `Run AI Employee watchers continuously`
   - Check: `Run when user logs on`
   - Check: `Run with highest privileges`

4. **Triggers Tab:**
   - Click **New**
   - Begin: `At log on`
   - Check: `Enabled`

5. **Actions Tab:**
   - Click **New**
   - Action: `Start a program`
   - Program: `C:\Users\YourName\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts\start_watchers.bat`
   - Start in: `C:\Users\YourName\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts`

6. **Conditions Tab:**
   - Uncheck: `Start only if computer is on AC power`
   - Check: `Wake the computer to run this task`

7. **Settings Tab:**
   - Check: `Allow task to be run on demand`
   - Check: `Run task as soon as possible after scheduled start is missed`
   - Uncheck: `Stop task if runs longer than`
   - Check: `If running, do not start a new instance`

8. Click **OK** and enter administrator password

**Option B: Using PowerShell**

```powershell
# Create scheduled task via PowerShell
$taskName = "AI Employee - Watchers"
$taskPath = "\AI Employee\"
$batchFile = "C:\Users\YourName\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts\start_watchers.bat"
$workingDir = "C:\Users\YourName\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts"

# Create task action
$action = New-ScheduledTaskAction -Execute $batchFile -WorkingDirectory $workingDir

# Create trigger (at log on)
$trigger = New-ScheduledTaskTrigger -AtLogOn

# Create settings
$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -WakeToRun `
    -ExecutionTimeLimit (New-TimeSpan -Hours 0) `
    -MultipleInstances IgnoreNew

# Create principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Register the task
Register-ScheduledTask `
    -TaskName $taskName `
    -TaskPath $taskPath `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal `
    -Description "Run AI Employee watchers continuously"

Write-Host "Task created successfully!"
```

## Setup: Daily Briefing Task

### Create PowerShell Script

Create `daily_briefing.ps1`:

```powershell
# daily_briefing.ps1
param(
    [string]$VaultPath = "C:\Users\YourName\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault"
)

Set-Location $VaultPath

# Generate daily briefing with Qwen Code
$qwenArgs = @(
    "Generate a daily briefing. Review:",
    "- Items completed yesterday in /Done",
    "- Pending items in /Needs_Action",
    "- Any approvals waiting in /Pending_Approval",
    "- Recent transactions in /Accounting",
    "",
    "Write the briefing to /Briefings/Daily_$(Get-Date -Format 'yyyy-MM-dd').md"
)

& qwen $qwenArgs

Write-Host "Daily briefing generated!"
```

### Schedule Daily Briefing

```powershell
$taskName = "AI Employee - Daily Briefing"
$psScript = "C:\Users\YourName\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault\scripts\daily_briefing.ps1"

$action = New-ScheduledTaskAction `
    -Execute "PowerShell.exe" `
    -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$psScript`""

$trigger = New-ScheduledTaskTrigger -Daily -At 8am

$settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -WakeToRun

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

Register-ScheduledTask `
    -TaskName $taskName `
    -TaskPath "\AI Employee\" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Principal $principal
```

## Task Management Commands

### View Tasks

```powershell
# List all AI Employee tasks
Get-ScheduledTask -TaskPath "\AI Employee\"

# View task details
Get-ScheduledTask -TaskName "AI Employee - Watchers" -TaskPath "\AI Employee\" | Format-List *
```

### Run Task Manually

```powershell
# Start a task immediately
Start-ScheduledTask -TaskName "AI Employee - Watchers" -TaskPath "\AI Employee\"
```

### Disable/Enable Task

```powershell
# Disable task
Disable-ScheduledTask -TaskName "AI Employee - Watchers" -TaskPath "\AI Employee\"

# Enable task
Enable-ScheduledTask -TaskName "AI Employee - Watchers" -TaskPath "\AI Employee\"
```

### Delete Task

```powershell
# Remove task
Unregister-ScheduledTask -TaskName "AI Employee - Watchers" -TaskPath "\AI Employee\" -Confirm
```

## Task Scheduler XML Export

Export task for backup or migration:

```powershell
Export-ScheduledTask -TaskName "AI Employee - Watchers" -TaskPath "\AI Employee\" | Out-File "AI_Employee_Watchers.xml"
```

Import on another machine:

```powershell
$taskXml = Get-Content "AI_Employee_Watchers.xml" | Out-String
Register-ScheduledTask -Xml $taskXml -TaskPath "\AI Employee\" -Force
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Task doesn't start | Check "Run with highest privileges" |
| Python not found | Use full path to python.exe |
| Task runs but nothing happens | Check working directory |
| Multiple instances running | Set "If running, do not start a new instance" |
| Task stops unexpectedly | Disable "Stop task if runs longer than" |

## Best Practices

1. **Log everything**: Redirect output to log files
2. **Error handling**: Add try-catch in scripts
3. **Resource limits**: Don't run too many tasks simultaneously
4. **Monitor tasks**: Check Task Scheduler regularly
5. **Update tasks**: Keep scripts and tasks in sync

## Example: Complete Setup Script

Create `setup_tasks.ps1`:

```powershell
# setup_tasks.ps1 - Complete AI Employee Task Scheduler Setup

$vaultPath = "C:\Users\YourName\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault"
$scriptsPath = "$vaultPath\scripts"
$taskPath = "\AI Employee\"

Write-Host "Setting up AI Employee Scheduled Tasks..."

# Create task folder
$schedule = New-Object -ComObject "Schedule.Service"
$schedule.Connect()
$rootFolder = $schedule.GetFolder("\")
try {
    $aiFolder = $rootFolder.GetFolder("AI Employee")
    Write-Host "Task folder already exists"
} catch {
    $aiFolder = $rootFolder.CreateFolder("AI Employee")
    Write-Host "Created task folder: AI Employee"
}

# Import tasks from XML (if you have exports)
# Or create programmatically as shown above

Write-Host "Setup complete!"
Write-Host "Tasks created in: $taskPath"
Write-Host "Run 'Get-ScheduledTask -TaskPath `"$taskPath`"' to view tasks"
```

## Next Steps

1. Set up continuous watchers
2. Schedule daily briefing
3. Configure weekly audit
4. Set up email notifications for task failures
5. Monitor task history regularly
