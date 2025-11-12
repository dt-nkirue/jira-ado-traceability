@echo off
echo ================================================
echo   Jira-ADO Traceability Report Generator
echo ================================================
echo.
echo Generating report...
echo.

cd /d "C:\Users\nkirue\AI-Playarea"
python jira_ado_traceability.py

echo.
echo ================================================
echo Report generation complete!
echo Check: Jira_ADO_Traceability_Report.xlsx
echo ================================================
echo.
pause
