# Gold Tier Health Check Script
# Comprehensive system health monitoring

$vaultPath = "C:\Users\a\Documents\GitHub\YT-Personal-AI-Employe-FTEs\AI_Employee_Vault"
$scriptsPath = "$vaultPath\scripts"
$odooPath = "C:\Users\a\Documents\GitHub\YT-Personal-AI-Employe-FTEs\odoo"
$logsPath = "$vaultPath\Logs"

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AI Employee - Gold Tier Health Check                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$overallScore = 0
$maxScore = 100

# 1. Check Docker (Odoo) - 20 points
Write-Host "1. Odoo ERP Status" -ForegroundColor Yellow
try {
    $odooStatus = docker-compose -C $odooPath ps 2>&1
    if ($odooStatus -match "Up") {
        Write-Host "   ✓ Odoo is running" -ForegroundColor Green
        $overallScore += 20
    } else {
        Write-Host "   ✗ Odoo is NOT running" -ForegroundColor Red
        Write-Host "     Fix: cd odoo && docker-compose up -d" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Docker check failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# 2. Check Python Processes - 20 points
Write-Host "2. Watcher Processes" -ForegroundColor Yellow
$watchers = @("ralph_wiggum_loop", "facebook_watcher", "gmail_watcher", "whatsapp_watcher", "filesystem_watcher")
$runningWatchers = 0

foreach ($watcher in $watchers) {
    $process = Get-Process | Where-Object { $_.CommandLine -like "*$watcher*" } 2>$null
    if ($process) {
        Write-Host "   ✓ $watcher running" -ForegroundColor Green
        $runningWatchers++
    } else {
        Write-Host "   - $watcher not running" -ForegroundColor Gray
    }
}

if ($runningWatchers -ge 2) {
    $overallScore += 20
} elseif ($runningWatchers -ge 1) {
    $overallScore += 10
}
Write-Host ""

# 3. Check MCP Servers - 15 points
Write-Host "3. MCP Servers" -ForegroundColor Yellow
$mcpServers = @("odoo_mcp_server", "facebook_mcp_server", "email_mcp_server")
$runningMCPs = 0

foreach ($mcp in $mcpServers) {
    $process = Get-Process | Where-Object { $_.CommandLine -like "*$mcp*" } 2>$null
    if ($process) {
        Write-Host "   ✓ $mcp running" -ForegroundColor Green
        $runningMCPs++
    } else {
        Write-Host "   - $mcp not running" -ForegroundColor Gray
    }
}

if ($runningMCPs -ge 2) {
    $overallScore += 15
} elseif ($runningMCPs -ge 1) {
    $overallScore += 8
}
Write-Host ""

# 4. Check Pending Approvals - 15 points
Write-Host "4. Pending Approvals" -ForegroundColor Yellow
$pendingFiles = Get-ChildItem "$vaultPath\Pending_Approval\*.md" -ErrorAction SilentlyContinue
$pendingCount = $pendingFiles.Count

if ($pendingCount -eq 0) {
    Write-Host "   ✓ No pending approvals" -ForegroundColor Green
    $overallScore += 15
} elseif ($pendingCount -le 5) {
    Write-Host "   ⚠ $pendingCount pending approval(s) - review needed" -ForegroundColor Yellow
    $overallScore += 10
    Write-Host "     Files:" -ForegroundColor Gray
    foreach ($file in $pendingFiles) {
        Write-Host "       - $($file.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "   ⚠⚠ $pendingCount pending approvals - attention required!" -ForegroundColor Red
    Write-Host "     Run: python approval_manager.py ..\ --list" -ForegroundColor Gray
}
Write-Host ""

# 5. Check Ralph Loop State - 15 points
Write-Host "5. Ralph Wiggum Loop" -ForegroundColor Yellow
$stateFiles = Get-ChildItem "$vaultPath\Plans\STATE_*.json" -ErrorAction SilentlyContinue
$activeTasks = 0
$completedTasks = 0

foreach ($stateFile in $stateFiles) {
    try {
        $state = Get-Content $stateFile | ConvertFrom-Json
        if ($state.status -eq "in_progress") {
            $activeTasks++
        } elseif ($state.status -eq "completed") {
            $completedTasks++
        }
    } catch {
        # Skip invalid files
    }
}

if ($activeTasks -eq 0) {
    Write-Host "   ✓ No stuck tasks" -ForegroundColor Green
    $overallScore += 15
} else {
    Write-Host "   ⚠ $activeTasks active task(s), $completedTasks completed" -ForegroundColor Yellow
    if ($activeTasks -le 2) {
        $overallScore += 12
    } else {
        $overallScore += 8
        Write-Host "     Consider reducing max_iterations if tasks are stuck" -ForegroundColor Gray
    }
}
Write-Host ""

# 6. Check Recent Logs - 15 points
Write-Host "6. Recent Activity (Last 24h)" -ForegroundColor Yellow
$today = Get-Date -Format "yyyy-MM-dd"
$logFile = Get-ChildItem "$logsPath\*-main.jsonl" -ErrorAction SilentlyContinue | Select-Object -First 1

if ($logFile) {
    try {
        $recentLogs = Get-Content $logFile.FullName | Select-Object -Last 50
        $errorCount = ($recentLogs | Select-String "error").Count
        $successCount = ($recentLogs | Select-String "success").Count
        
        Write-Host "   Last log: $($logFile.Name)" -ForegroundColor Gray
        Write-Host "   Recent errors: $errorCount" -ForegroundColor $(if ($errorCount -gt 5) {"Red"} else {"Green"})
        Write-Host "   Recent successes: $successCount" -ForegroundColor Green
        
        if ($errorCount -le 5) {
            $overallScore += 15
        } elseif ($errorCount -le 10) {
            $overallScore += 10
            Write-Host "   ⚠ Consider reviewing error logs" -ForegroundColor Yellow
        } else {
            Write-Host "   ⚠⚠ High error rate - review logs!" -ForegroundColor Red
        }
    } catch {
        Write-Host "   - Could not read logs" -ForegroundColor Gray
    }
} else {
    Write-Host "   - No log files found" -ForegroundColor Gray
}
Write-Host ""

# 7. Disk Space Check - Bonus
Write-Host "7. System Resources" -ForegroundColor Yellow
$disk = Get-PSDrive -Name (Get-Item $vaultPath).PSDrive.Name
$freeGB = [math]::Round($disk.Free / 1GB, 2)

if ($freeGB -gt 10) {
    Write-Host "   ✓ Disk space: ${freeGB}GB free" -ForegroundColor Green
} elseif ($freeGB -gt 5) {
    Write-Host "   ⚠ Disk space: ${freeGB}GB free (consider cleanup)" -ForegroundColor Yellow
} else {
    Write-Host "   ⚠⚠ Disk space: ${freeGB}GB free (critical!)" -ForegroundColor Red
}

$memory = Get-CimInstance Win32_OperatingSystem
$freeMemory = [math]::Round($memory.FreePhysicalMemory / 1MB, 2)
Write-Host "   Memory: ${freeMemory}GB free" -ForegroundColor $(if ($freeMemory -gt 4) {"Green"} else {"Yellow"})
Write-Host ""

# Overall Score
Write-Host "╔════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                    HEALTH SCORE                        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$percentage = ($overallScore / $maxScore) * 100

if ($percentage -ge 80) {
    Write-Host "   Score: $overallScore / $maxScore ($([math]::Round($percentage, 1))%)" -ForegroundColor Green
    Write-Host "   Status: ✓ System Healthy" -ForegroundColor Green
} elseif ($percentage -ge 60) {
    Write-Host "   Score: $overallScore / $maxScore ($([math]::Round($percentage, 1))%)" -ForegroundColor Yellow
    Write-Host "   Status: ⚠ System Needs Attention" -ForegroundColor Yellow
} else {
    Write-Host "   Score: $overallScore / $maxScore ($([math]::Round($percentage, 1))%)" -ForegroundColor Red
    Write-Host "   Status: ✗ System Unhealthy" -ForegroundColor Red
}

Write-Host ""
Write-Host "Recommendations:" -ForegroundColor Cyan

if ($overallScore -lt $maxScore) {
    if ($odooStatus -notmatch "Up") {
        Write-Host "  1. Start Odoo: cd odoo && docker-compose up -d" -ForegroundColor Yellow
    }
    if ($runningWatchers -lt 2) {
        Write-Host "  2. Start watchers: python start_gold_tier.bat" -ForegroundColor Yellow
    }
    if ($pendingCount -gt 0) {
        Write-Host "  3. Review approvals: python approval_manager.py ..\ --list" -ForegroundColor Yellow
    }
    if ($activeTasks -gt 2) {
        Write-Host "  4. Check stuck tasks: cat Plans\STATE_*.json" -ForegroundColor Yellow
    }
} else {
    Write-Host "  All systems operational! No action needed." -ForegroundColor Green
}

Write-Host ""
Write-Host "Quick Commands:" -ForegroundColor Cyan
Write-Host "  - View dashboard: cat ..\Dashboard.md" -ForegroundColor Gray
Write-Host "  - View briefings: cat ..\Briefings\*.md" -ForegroundColor Gray
Write-Host "  - Check Odoo: docker-compose ps" -ForegroundColor Gray
Write-Host "  - View logs: cat Logs\*-main.jsonl" -ForegroundColor Gray
Write-Host ""

# Export report
$reportPath = "$logsPath\health_check_$(Get-Date -Format 'yyyy-MM-dd_HHmmss').txt"
Write-Host "Report saved to: $reportPath" -ForegroundColor Gray

# Create report content
$report = @"
AI Employee Gold Tier - Health Check Report
Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Score: $overallScore / $maxScore ($([math]::Round($percentage, 1))%)

Details:
- Odoo Status: $(if ($odooStatus -match "Up") {"Running"} else {"Not Running"})
- Running Watchers: $runningWatchers
- Running MCPs: $runningMCPs
- Pending Approvals: $pendingCount
- Active Ralph Tasks: $activeTasks
- Completed Ralph Tasks: $completedTasks
- Free Disk Space: ${freeGB}GB
- Free Memory: ${freeMemory}GB
"@

$report | Out-File -FilePath $reportPath -Encoding UTF8
