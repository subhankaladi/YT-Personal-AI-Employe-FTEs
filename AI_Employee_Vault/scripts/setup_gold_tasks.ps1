# Gold Tier Windows Task Scheduler Setup
# Creates scheduled tasks for Gold Tier components

$taskPath = "\AI Employee\Gold Tier\"
$vaultPath = "C:\Users\a\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault"
$scriptsPath = "$vaultPath\scripts"
$odooPath = "C:\Users\a\Documents\GitHub\YT-Personal-AI-Employe-FTEs\odoo"

Write-Host "AI Employee Gold Tier - Task Scheduler Setup"
Write-Host "============================================="
Write-Host ""

# Create task path
New-Item -ItemType Directory -Force -Path "Microsoft$taskPath" | Out-Null

# 1. Weekly CEO Briefing - Every Monday at 7:00 AM
Write-Host "Creating: Weekly CEO Briefing task..."
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "ceo_briefing_generator.py ..\" `
  -WorkingDirectory $scriptsPath

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 7am

$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType S4U -RunLevel Highest

Register-ScheduledTask -TaskPath $taskPath `
  -TaskName "Weekly CEO Briefing" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Force | Out-Null

Write-Host "  ✓ Weekly CEO Briefing scheduled (Monday 7:00 AM)"

# 2. Daily Briefing - Every day at 8:00 AM
Write-Host "Creating: Daily Briefing task..."
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "ceo_briefing_generator.py ..\ --week-start (Get-Date).AddDays(-1).ToString('yyyy-MM-dd') --week-end (Get-Date).AddDays(-1).ToString('yyyy-MM-dd')" `
  -WorkingDirectory $scriptsPath

$trigger = New-ScheduledTaskTrigger -Daily -At 8am

Register-ScheduledTask -TaskPath $taskPath `
  -TaskName "Daily Briefing" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Force | Out-Null

Write-Host "  ✓ Daily Briefing scheduled (8:00 AM)"

# 3. Gold Orchestrator - At log on (continuous)
Write-Host "Creating: Gold Orchestrator task..."
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "ralph_wiggum_loop.py ..\ --orchestrator --interval 30" `
  -WorkingDirectory $scriptsPath

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
  -AllowStartIfOnBatteries `
  -DontStopIfGoingOnBatteries `
  -ExecutionTimeLimit (New-TimeSpan -Hours 24) `
  -RestartCount 3 `
  -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskPath $taskPath `
  -TaskName "Gold Orchestrator" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Settings $settings `
  -Force | Out-Null

Write-Host "  ✓ Gold Orchestrator scheduled (At log on, continuous)"

# 4. Odoo Health Check - Every hour
Write-Host "Creating: Odoo Health Check task..."
$action = New-ScheduledTaskAction -Execute "docker-compose" `
  -Argument "ps" `
  -WorkingDirectory $odooPath

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 1)

$scriptContent = @"
cd "$odooPath"
`$result = docker-compose ps
if (`$result -notmatch "Up") {
    Write-Host "$(Get-Date): Odoo not running, attempting restart..." 
    docker-compose restart
}
"@

$scriptPath = "$scriptsPath\odoo_health_check.ps1"
$scriptContent | Out-File -FilePath $scriptPath -Encoding UTF8

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""

Register-ScheduledTask -TaskPath $taskPath `
  -TaskName "Odoo Health Check" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Force | Out-Null

Write-Host "  ✓ Odoo Health Check scheduled (Every hour)"

# 5. Approval Reminder - Every 4 hours
Write-Host "Creating: Approval Reminder task..."
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "approval_manager.py ..\ --list" `
  -WorkingDirectory $scriptsPath

$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Hours 4)

Register-ScheduledTask -TaskPath $taskPath `
  -TaskName "Approval Reminder" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Force | Out-Null

Write-Host "  ✓ Approval Reminder scheduled (Every 4 hours)"

# 6. Log Cleanup - Weekly on Sunday at 11:00 PM
Write-Host "Creating: Log Cleanup task..."
$scriptContent = @"
# Clean up logs older than 90 days
$logsPath = "$vaultPath\Logs"
$cutoff = (Get-Date).AddDays(-90)

Get-ChildItem -Path $logsPath -File | Where-Object { `$_.LastWriteTime -lt $cutoff } | Remove-Item -Force
Write-Host "$(Get-Date): Cleaned up logs older than 90 days"
"@

$scriptPath = "$scriptsPath\log_cleanup.ps1"
$scriptContent | Out-File -FilePath $scriptPath -Encoding UTF8

$action = New-ScheduledTaskAction -Execute "powershell.exe" `
  -Argument "-ExecutionPolicy Bypass -File `"$scriptPath`""

$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 11pm

Register-ScheduledTask -TaskPath $taskPath `
  -TaskName "Log Cleanup" `
  -Action $action `
  -Trigger $trigger `
  -Principal $principal `
  -Force | Out-Null

Write-Host "  ✓ Log Cleanup scheduled (Sunday 11:00 PM)"

Write-Host ""
Write-Host "============================================="
Write-Host "Gold Tier Task Scheduler Setup Complete!"
Write-Host ""
Write-Host "Scheduled Tasks:"
Write-Host "  - Weekly CEO Briefing (Monday 7:00 AM)"
Write-Host "  - Daily Briefing (8:00 AM)"
Write-Host "  - Gold Orchestrator (At log on, continuous)"
Write-Host "  - Odoo Health Check (Every hour)"
Write-Host "  - Approval Reminder (Every 4 hours)"
Write-Host "  - Log Cleanup (Sunday 11:00 PM)"
Write-Host ""
Write-Host "To view tasks:"
Write-Host "  Get-ScheduledTask -TaskPath '\AI Employee\Gold Tier\'"
Write-Host ""
Write-Host "To run a task manually:"
Write-Host "  Start-ScheduledTask -TaskPath '\AI Employee\Gold Tier\' -TaskName 'Task Name'"
Write-Host ""
Write-Host "To remove all Gold Tier tasks:"
Write-Host "  Get-ScheduledTask -TaskPath '\AI Employee\Gold Tier\' | Unregister-ScheduledTask -Confirm:`$false"
