# FinancePulse Data Refresh Setup

## Cronjob Setup (Alternative to launchd)

Add these lines to your crontab (`crontab -e`):

```bash
# Daily refresh at 8:00 AM (Monday-Friday)
0 8 * * 1-5 /Users/jasonlee/Desktop/FinancePulse/finance-pulse/scripts/refresh_data.sh

# After-market refresh at 4:30 PM (Monday-Friday)
30 16 * * 1-5 /Users/jasonlee/Desktop/FinancePulse/finance-pulse/scripts/refresh_data.sh
```

## launchd Setup (Recommended for macOS)

1. Copy the plist file to LaunchAgents:
```bash
cp com.financepulse.daily.plist ~/Library/LaunchAgents/
```

2. Load the agent:
```bash
launchctl load ~/Library/LaunchAgents/com.financepulse.daily.plist
```

3. Verify it's loaded:
```bash
launchctl list | grep financepulse
```

## Skills Execution

The actual Skills execution would be implemented here. The Skills would:
1. Execute in parallel for faster data collection
2. Output JSON files to `~/.hermes/daily-report/`
3. Support the 20 financial Skills from the PRD
