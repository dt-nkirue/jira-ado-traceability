# Jira-ADO Traceability Skill

Generate comprehensive traceability reports between Jira issues and Azure DevOps work items.

## What This Skill Does

This skill creates an Excel report that:
1. Fetches all Jira issues from a specified project
2. Identifies linked Azure DevOps work items via the "AzureDevOps ID" custom field
3. Retrieves detailed information from Azure DevOps/TFS
4. Compares status, severity, and assignee between both systems
5. Generates a comprehensive Excel report with 6 sheets:
   - Summary (overall statistics)
   - Full Traceability (all items)
   - Mismatches (discrepancies only)
   - Matched Items (all linked items)
   - Matched Summary (detailed linked item statistics)
   - Unlinked Issues (Jira items without ADO links)

## Required Information

When using this skill, you'll need to provide:

### Jira Credentials
- **Jira Cloud URL**: Your Atlassian instance (e.g., https://yourcompany.atlassian.net)
- **Email**: Your Jira account email
- **API Token**: Jira API token from https://id.atlassian.com/manage-profile/security/api-tokens
- **Project Key**: The Jira project code (e.g., "GRA", "PROJ")

### Azure DevOps Credentials
- **TFS/ADO Server URL**: Your TFS server base URL (e.g., http://tfsserver:8080/tfs)
- **Collection**: TFS collection name (e.g., "Iho")
- **Project**: ADO project name (e.g., "Guyana")
- **Personal Access Token (PAT)**: Azure DevOps PAT with work item read permissions

### Output Location
- **Output Directory**: Where to save the Excel report (default: current working directory)
- **Report Name**: Custom report filename (optional, default: Jira_ADO_Traceability_Report.xlsx)

## How to Use

Simply invoke this skill and provide the required credentials. The skill will:
1. Validate the connection to both Jira and Azure DevOps
2. Fetch all relevant data
3. Perform comparison analysis
4. Generate the Excel report
5. Provide summary statistics

## Report Metrics

The report includes:
- **Linkage**: Total issues, linked vs unlinked counts
- **Status Comparison**: Identifies when Jira and ADO status don't match
- **Severity Comparison**: Flags severity discrepancies
- **Assignee Comparison**: Highlights different assignees
- **Time Metrics**: Creation dates, resolution dates
- **Detailed Breakdowns**: By status, severity, assignee, work item type

## Example Usage

```
skill: jira-ado-traceability
```

Then follow the prompts to provide:
- Jira URL, email, API token, project key
- ADO server URL, collection, project, PAT
- Output directory (optional)

The skill will generate a comprehensive Excel report showing full traceability between Jira and Azure DevOps.

## Security Notes

- API tokens and PATs are used only for the current session
- Credentials are not stored permanently
- All API calls use secure authentication (Basic Auth with tokens)
- Consider using environment variables for credentials in repeated use

## Troubleshooting

If the skill fails:
1. Verify Jira API token is valid and has read permissions
2. Verify ADO PAT has work item read access
3. Check network connectivity to both Jira Cloud and TFS server
4. Ensure the custom field "AzureDevOps ID" (customfield_10109) exists in your Jira instance
5. Check that the project key is correct

## Maintenance

The skill uses the Python script: `jira_ado_traceability.py`
Located at: `C:\Users\nkirue\AI-Playarea\jira_ado_traceability.py`

To customize:
- Modify comparison logic for status/severity matching
- Add additional custom fields to fetch
- Adjust Excel formatting and styling
- Add more comparison metrics
