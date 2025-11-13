# Jira-ADO Traceability Robot Setup Instructions

## Overview

This robot automatically generates Jira-ADO traceability reports on a scheduled basis. It can run daily, weekly, or at any custom interval using Windows Task Scheduler.

---

## 1. Prerequisites

### Required Software
- Python 3.7 or higher
- Required Python packages (install via requirements.txt)

### Required Data
- Azure DevOps (TFS) Personal Access Token
- Jira data export file (JSON format)

---

## 2. Installation Steps

### Step 1: Install Python Dependencies

```bash
cd C:\Users\nkirue\AI-Playarea\jira-ado-traceability-project
pip install -r requirements.txt
```

If you don't have a requirements.txt yet, install manually:

```bash
pip install pandas requests openpyxl fuzzywuzzy python-Levenshtein
```

### Step 2: Create Configuration File

1. Copy the example configuration:
   ```bash
   copy config.example.json config.json
   ```

2. Edit `config.json` with your settings:
   - **ADO Configuration**: Update server URL, collection, project, and PAT
   - **Jira Data File**: Path to your Jira export JSON file
   - **Output Directory**: Where reports will be saved
   - **Logging**: Where logs will be stored

**Example config.json:**
```json
{
  "ado": {
    "server": "http://tfsserver:8080/tfs",
    "collection": "YourCollection",
    "project": "YourProject",
    "pat": "your-ado-pat-here-or-use-env-variable"
  },
  "jira": {
    "data_file": "C:\\path\\to\\jira_with_ado.json"
  },
  "output": {
    "report_directory": "C:\\Reports\\Jira-ADO",
    "report_filename": "Jira_ADO_Traceability_Report_{timestamp}.xlsx"
  },
  "fuzzy_matching": {
    "enabled": true,
    "min_score": 70,
    "max_ado_items": 200,
    "days_lookback": 90
  },
  "logging": {
    "log_directory": "C:\\Logs\\Jira-ADO",
    "log_level": "INFO"
  }
}
```

### Step 3: Secure Your Credentials (Recommended)

Instead of storing your ADO PAT in the config file, use environment variables:

1. Open System Properties > Advanced > Environment Variables
2. Add a new User or System variable:
   - **Name**: `ADO_PAT`
   - **Value**: Your Azure DevOps Personal Access Token

3. Set `config.json` ADO PAT to empty string:
   ```json
   "pat": ""
   ```

The robot will automatically read from the `ADO_PAT` environment variable.

### Step 4: Test Manual Execution

Before scheduling, test the robot manually:

```bash
cd C:\Users\nkirue\AI-Playarea\jira-ado-traceability-project
python jira_ado_traceability_scheduled.py
```

Or using the batch file:

```bash
run_traceability_robot.bat
```

**Expected Output:**
- Console logs showing progress
- Log file created in the configured logging directory
- Excel report created in the configured output directory

---

## 3. Schedule with Windows Task Scheduler

### Option A: Using Task Scheduler GUI

1. **Open Task Scheduler**
   - Press `Win + R`, type `taskschd.msc`, press Enter

2. **Create Basic Task**
   - Click "Create Basic Task..." in the Actions panel
   - Name: `Jira-ADO Traceability Robot`
   - Description: `Automated Jira-ADO traceability report generation`

3. **Set Trigger**
   - Choose frequency: Daily, Weekly, Monthly, etc.
   - Example: Daily at 8:00 AM

4. **Set Action**
   - Action: "Start a program"
   - Program/script: `C:\Users\nkirue\AI-Playarea\jira-ado-traceability-project\run_traceability_robot.bat`
   - Start in: `C:\Users\nkirue\AI-Playarea\jira-ado-traceability-project`

5. **Configure Advanced Settings**
   - Check "Run whether user is logged on or not" (recommended for servers)
   - Check "Run with highest privileges" (if needed for file access)
   - Configure for: Windows 10

6. **Test the Task**
   - Right-click the task > "Run"
   - Check logs to verify successful execution

### Option B: Using PowerShell (Automated Setup)

Run this PowerShell script as Administrator:

```powershell
# Define task parameters
$TaskName = "Jira-ADO Traceability Robot"
$Description = "Automated Jira-ADO traceability report generation"
$ScriptPath = "C:\Users\nkirue\AI-Playarea\jira-ado-traceability-project\run_traceability_robot.bat"
$WorkingDir = "C:\Users\nkirue\AI-Playarea\jira-ado-traceability-project"

# Create action
$Action = New-ScheduledTaskAction -Execute $ScriptPath -WorkingDirectory $WorkingDir

# Create trigger (Daily at 8:00 AM)
$Trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

# Create principal (run as current user)
$Principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType S4U

# Create settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Register task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Principal $Principal -Settings $Settings -Description $Description
```

### Option C: Using Command Line (schtasks)

```cmd
schtasks /create /tn "Jira-ADO Traceability Robot" /tr "C:\Users\nkirue\AI-Playarea\jira-ado-traceability-project\run_traceability_robot.bat" /sc daily /st 08:00 /ru "%USERNAME%" /rl HIGHEST
```

---

## 4. Schedule Options

### Common Schedules

**Daily at 8:00 AM:**
```
Trigger: Daily
Start time: 8:00 AM
```

**Every Weekday at 9:00 AM:**
```
Trigger: Weekly
Days: Monday, Tuesday, Wednesday, Thursday, Friday
Start time: 9:00 AM
```

**Every Monday at 7:00 AM:**
```
Trigger: Weekly
Days: Monday
Start time: 7:00 AM
```

**Multiple times per day (every 4 hours):**
```
Trigger: Daily
Start time: 8:00 AM
Repeat task every: 4 hours
For a duration of: 1 day
```

---

## 5. Monitoring and Maintenance

### Check Execution Status

1. **View Task History**
   - Open Task Scheduler
   - Select your task
   - Click "History" tab (enable if disabled)

2. **Check Logs**
   - Logs are stored in the directory specified in `config.json`
   - Each run creates a timestamped log file
   - Example: `jira_ado_traceability_20250114_080000.log`

3. **Check Reports**
   - Reports are saved in the output directory specified in `config.json`
   - Each report is timestamped
   - Example: `Jira_ADO_Traceability_Report_20250114_080000.xlsx`

### Troubleshooting

**Problem: Task shows "Running" but nothing happens**
- Check that Python is in the system PATH
- Verify the batch file paths are correct
- Run the batch file manually to see errors

**Problem: "Access Denied" errors**
- Run Task Scheduler as Administrator
- Check file/folder permissions for output and log directories
- Ensure the task is configured to "Run with highest privileges"

**Problem: Reports not generated**
- Check log files for errors
- Verify ADO PAT is valid and has correct permissions
- Ensure Jira data file exists and is accessible
- Check network connectivity to ADO server

**Problem: Task fails silently**
- Enable task history in Task Scheduler
- Check Windows Event Viewer (Applications and Services Logs > Microsoft > Windows > TaskScheduler)
- Verify environment variables are set correctly

### Email Notifications (Optional)

To receive email notifications when reports are generated, configure the `notifications` section in `config.json`:

```json
{
  "notifications": {
    "enabled": true,
    "email": {
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "from_address": "robot@example.com",
      "to_addresses": ["user1@example.com", "user2@example.com"],
      "username": "your-smtp-username",
      "password": "your-smtp-password"
    }
  }
}
```

Or use environment variables:
- `SMTP_USERNAME`
- `SMTP_PASSWORD`

---

## 6. Configuration Reference

### Full Configuration Options

```json
{
  "ado": {
    "server": "http://tfsserver:8080/tfs",
    "collection": "DefaultCollection",
    "project": "MyProject",
    "pat": ""  // Use ADO_PAT environment variable
  },
  "jira": {
    "data_file": "C:\\path\\to\\jira_with_ado.json"
  },
  "output": {
    "report_directory": "C:\\Reports",
    "report_filename": "Jira_ADO_Traceability_Report_{timestamp}.xlsx"
  },
  "fuzzy_matching": {
    "enabled": true,          // Enable/disable fuzzy matching
    "min_score": 70,          // Minimum match score (0-100)
    "max_ado_items": 200,     // Max ADO items to fetch for matching
    "days_lookback": 90       // How far back to search for ADO items
  },
  "logging": {
    "log_directory": "C:\\Logs",
    "log_level": "INFO"       // DEBUG, INFO, WARNING, ERROR, CRITICAL
  },
  "notifications": {
    "enabled": false,
    "email": {
      "smtp_server": "smtp.example.com",
      "smtp_port": 587,
      "from_address": "robot@example.com",
      "to_addresses": ["user@example.com"],
      "username": "",         // Use SMTP_USERNAME env variable
      "password": ""          // Use SMTP_PASSWORD env variable
    }
  }
}
```

### Environment Variables

The robot supports these environment variables (override config.json):

- `ADO_PAT` - Azure DevOps Personal Access Token
- `JIRA_DATA_FILE` - Path to Jira JSON export file
- `JIRA_ADO_CONFIG` - Path to config.json file (if not in script directory)
- `SMTP_USERNAME` - SMTP username for email notifications
- `SMTP_PASSWORD` - SMTP password for email notifications

---

## 7. Best Practices

1. **Security**
   - Never commit `config.json` with credentials to version control
   - Use environment variables for sensitive data
   - Store PAT securely in Windows Credential Manager or environment variables

2. **Scheduling**
   - Schedule during off-peak hours to minimize server load
   - Don't schedule too frequently (daily is usually sufficient)
   - Consider time zones if working with global teams

3. **Monitoring**
   - Regularly check logs for errors
   - Set up email notifications for failures
   - Archive old reports periodically

4. **Maintenance**
   - Update Python dependencies periodically
   - Rotate ADO PAT before expiration
   - Keep Jira data export up to date

5. **Testing**
   - Always test manually before scheduling
   - Verify reports are generated correctly
   - Check that all ADO work items are accessible

---

## 8. Support and Troubleshooting

### Log Analysis

Logs contain detailed information about each run:

```
2025-01-14 08:00:00 - JiraAdoRobot - INFO - Jira-ADO Traceability Robot Starting
2025-01-14 08:00:01 - JiraAdoRobot - INFO - Loading Jira data from: C:\...\jira_with_ado.json
2025-01-14 08:00:02 - JiraAdoRobot - INFO - Loaded 150 Jira issues
2025-01-14 08:00:03 - JiraAdoRobot - INFO - Fetching Azure DevOps work items...
...
2025-01-14 08:01:30 - JiraAdoRobot - INFO - EXECUTION SUCCESSFUL
```

Look for `ERROR` or `WARNING` messages to diagnose issues.

### Common Exit Codes

- `0` - Success
- `1` - Failure (check logs for details)

### Getting Help

If you encounter issues:

1. Check log files for error messages
2. Verify configuration settings
3. Test ADO connectivity manually
4. Ensure all Python dependencies are installed
5. Check Windows Event Viewer for system-level errors

---

## Files Overview

```
jira-ado-traceability-project/
├── jira_ado_traceability_scheduled.py  # Main robot script
├── run_traceability_robot.bat          # Windows batch wrapper
├── config.example.json                 # Example configuration
├── config.json                         # Your configuration (create this)
├── SETUP_INSTRUCTIONS.md               # This file
├── requirements.txt                    # Python dependencies (create if needed)
└── README.md                           # Project documentation
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Create and configure `config.json`
3. ✅ Test manual execution
4. ✅ Schedule with Task Scheduler
5. ✅ Monitor first few runs
6. ✅ Set up notifications (optional)

**Your robot is now ready to run on schedule!** 🤖
