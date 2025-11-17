@echo off
REM Jira-ADO Traceability Robot Runner
REM This script is designed to be run by Windows Task Scheduler

REM Set working directory to script location
cd /d "%~dp0"

REM Set environment variables (if needed)
REM Uncomment and configure these if you want to override config.json values
REM SET ADO_PAT=your-personal-access-token-here
REM SET JIRA_DATA_FILE=C:\path\to\jira_with_ado.json
REM SET JIRA_ADO_CONFIG=C:\path\to\config.json

REM Run the robot using just command
echo Starting Jira-ADO Traceability Robot...
echo Timestamp: %date% %time%
echo.

just run-scheduled

REM Capture exit code
SET EXIT_CODE=%ERRORLEVEL%

echo.
echo Robot finished with exit code: %EXIT_CODE%
echo Timestamp: %date% %time%

REM Exit with the same code as the Python script
exit /b %EXIT_CODE%
