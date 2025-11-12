# Jira-ADO Traceability Skill

A comprehensive skill for generating traceability reports between Jira issues and Azure DevOps work items.

## Overview

This skill automates the process of:
- Fetching Jira issues from your project
- Retrieving linked Azure DevOps work items
- Comparing status, severity, and assignee between systems
- Generating detailed Excel reports with multiple analysis sheets

## Quick Start

To use this skill in Claude Code:

```bash
skill: jira-ado-traceability
```

Or use the Skill tool and specify:
```
Skill: jira-ado-traceability
```

## What You'll Need

### Jira Credentials
1. Your Jira Cloud URL (e.g., https://yourcompany.atlassian.net)
2. Your Jira email address
3. Jira API Token (generate at: https://id.atlassian.com/manage-profile/security/api-tokens)
4. Project Key (e.g., "GRA", "PROJ")

### Azure DevOps Credentials
1. TFS/ADO Server URL (e.g., http://tfsserver:8080/tfs)
2. Collection name (e.g., "Iho")
3. Project name (e.g., "Guyana")
4. Personal Access Token (PAT) with work item read permissions

## Report Output

The skill generates an Excel file with **6 comprehensive sheets**:

### 1. Summary
High-level statistics including:
- Total issues count
- Linked vs unlinked breakdown
- Mismatch counts and percentages
- Status, priority, and issue type distributions

### 2. Full Traceability
Complete dataset showing:
- All Jira fields (Key, Summary, Status, Priority, Severity, Assignee, Dates)
- All ADO fields (ID, Title, State, Work Item Type, Priority, Severity, Assignee, Dates)
- Comparison results (Status, Severity, Assignee)

### 3. Mismatches
Filtered view of items with discrepancies:
- Status misalignment (Jira closed but ADO open, etc.)
- Severity differences
- Different assignees

### 4. Matched Items
All 54 items that have ADO links:
- Full traceability information
- Comparison indicators
- Helps identify which linked items need attention

### 5. Matched Summary
Detailed analytics for linked items:
- Total linked count and percentages
- Comparison quality metrics
- Status/Severity/Assignee match rates
- Breakdowns by various dimensions
- Top 10 assignees

### 6. Unlinked Issues
Jira issues without ADO connections:
- Key, Summary, Status, Severity, Assignee
- Highlights gaps in traceability

## Features

✅ **Automatic Data Fetching** - Connects to both Jira and ADO APIs
✅ **Smart Comparison** - Intelligently compares status, severity, and assignee
✅ **Comprehensive Reporting** - 6 different views for different audiences
✅ **Visual Formatting** - Color-coded headers and formatted columns
✅ **Error Handling** - Graceful handling of missing data or connection issues
✅ **Reusable** - Save credentials for repeated runs

## Use Cases

- **UAT Testing**: Track testing issues across systems
- **Sprint Planning**: Understand work item distribution
- **Compliance Audits**: Generate traceability documentation
- **Status Sync**: Identify synchronization issues
- **Severity Validation**: Ensure consistent priority across tools
- **Team Coordination**: Monitor assignee alignment

## Technical Details

### Python Dependencies
- `pandas` - Data manipulation and analysis
- `openpyxl` - Excel file generation
- `requests` - API communication

### Custom Fields Used
- `customfield_10042` - Severity (Jira)
- `customfield_10109` - AzureDevOps ID (Jira)
- `customfield_10110` - AzureDevOps State (Jira)

### Comparison Logic

**Status Comparison:**
- Checks if both systems show "closed/done" or both show "open/in progress"
- Flags misalignment when one is closed and the other is open

**Severity Comparison:**
- Extracts numeric values from both systems
- Jira format: "Sev-4" → "4"
- ADO format: Direct numeric
- Compares for equality

**Assignee Comparison:**
- Case-insensitive display name matching
- Flags when assignees differ between systems

## Customization

The skill is built on `traceability_template.py` which you can customize:

1. **Add more fields**: Include additional Jira or ADO fields
2. **Adjust comparison logic**: Modify how status/severity matching works
3. **Change Excel styling**: Update colors, fonts, column widths
4. **Add charts**: Include visualizations in the Excel report
5. **Filter criteria**: Focus on specific issue types or priorities

## Troubleshooting

### Common Issues

**"Could not connect to Jira"**
- Verify your API token is valid
- Check the Jira URL format
- Ensure you have read permissions on the project

**"Failed to fetch ADO work item"**
- Confirm your PAT has work item read access
- Verify TFS server is accessible from your network
- Check that the ADO ID in Jira is valid

**"No items in Matched tabs"**
- This was the original bug - now fixed!
- Matched items = any Jira issue with an ADO ID
- Check if issues actually have ADO IDs populated

**"Severity mismatches: 100%"**
- This is expected if severity formats differ significantly
- Consider customizing the severity comparison logic
- Map known severity values between systems

## Security Best Practices

- ✅ API tokens are used only during execution
- ✅ No credentials stored in code or config files
- ✅ Use environment variables for repeated runs
- ✅ Regularly rotate API tokens and PATs
- ✅ Limit PAT permissions to minimum required (work item read only)

## Version History

### v1.0.0 (Current)
- Initial release
- Support for Jira Cloud and TFS/Azure DevOps Server
- 6-sheet Excel report
- Status, severity, and assignee comparison
- Linked vs unlinked analysis

## Support

For issues, customizations, or questions:
1. Check the skill.md documentation
2. Review the prompt.md for detailed instructions
3. Examine traceability_template.py for implementation details
4. Modify configuration in the Python script as needed

## License

This skill is part of your Claude Code workspace and can be freely modified for your needs.
