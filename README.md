# Jira-ADO Traceability System

A comprehensive Python-based tool for generating traceability reports between Jira issues and Azure DevOps (TFS) work items with intelligent fuzzy matching for unlinked items.

## 🎯 Features

- **Automated Data Fetching** - Connects to both Jira Cloud and Azure DevOps/TFS APIs
- **Comprehensive Comparison** - Analyzes status, severity, and assignee alignment
- **Fuzzy Matching** - Intelligent title-based matching for unlinked items (≥70% confidence)
- **Excel Report Generation** - Creates detailed 7-sheet Excel reports
- **Visual Analytics** - Color-coded sheets with formatted data
- **Reusable Configuration** - Save credentials for repeated runs

## 📊 Report Sheets

The tool generates an Excel file with 7 comprehensive sheets:

1. **Summary** - High-level statistics and key metrics
2. **Full Traceability** - Complete mapping of all Jira issues to ADO work items
3. **Mismatches** - Items with status, severity, or assignee discrepancies
4. **Matched Items** - All Jira issues successfully linked to ADO
5. **Matched Summary** - Detailed analytics for linked items
6. **Potential Matches** - Fuzzy-matched suggestions for unlinked items
7. **Unlinked Issues** - Jira items without ADO connections

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Jira Cloud account with API access
- Azure DevOps/TFS server access
- Required Python packages (see Installation)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jira-ado-traceability-project.git
cd jira-ado-traceability-project

# Install required packages
pip install -r requirements.txt
```

### Configuration

Edit `jira_ado_traceability.py` and update the configuration section:

```python
# Jira Configuration
JIRA_URL = "https://yourcompany.atlassian.net"
JIRA_EMAIL = "your.email@company.com"
JIRA_API_TOKEN = "your-jira-api-token"
PROJECT_KEY = "GRA"

# Azure DevOps Configuration
ADO_SERVER = "http://tfsserver:8080/tfs"
ADO_COLLECTION = "Iho"
ADO_PROJECT = "Guyana"
ADO_PAT = "your-ado-personal-access-token"
```

### Usage

**Option 1: Python Command**
```bash
python jira_ado_traceability.py
```

**Option 2: Batch File (Windows)**
```bash
run_traceability_report.bat
```

**Option 3: Claude Code Skill**
```
skill: jira-ado-traceability
```

## 📋 What Gets Tracked

### Jira Fields
- Key, Summary, Status, Priority
- Issue Type, Severity
- Assignee, Reporter
- Created Date, Resolution Date
- Custom Fields: AzureDevOps ID, AzureDevOps State

### Azure DevOps Fields
- Work Item ID, Title, State
- Work Item Type, Priority, Severity
- Assigned To
- Created Date, Closed Date, Resolved Date
- Area Path, Iteration Path

### Comparison Metrics
- **Status Alignment** - Both closed, both open, or mismatched
- **Severity Matching** - Numeric severity comparison
- **Assignee Consistency** - Display name matching
- **Fuzzy Title Matching** - 70%+ similarity for unlinked items

## 🔍 Fuzzy Matching

The tool uses intelligent fuzzy matching to suggest potential links:

- **Algorithm**: Token sort ratio (handles word order differences)
- **Threshold**: 70% minimum similarity
- **Confidence Levels**:
  - 🟢 Very High (90-100%)
  - 🟢 High (80-89%)
  - 🟡 Medium (70-79%)
- **Scan Scope**: Last 90 days of ADO work items
- **Match Limit**: Top 5 suggestions per Jira item

## 📦 Project Structure

```
jira-ado-traceability-project/
├── jira_ado_traceability.py       # Main Python script
├── run_traceability_report.bat    # Windows batch launcher
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── LICENSE                         # MIT License
├── .gitignore                      # Git ignore rules
├── skill/                          # Claude Code skill files
│   ├── skill.md                    # Skill documentation
│   ├── prompt.md                   # Skill instructions
│   ├── skill.json                  # Skill configuration
│   ├── README.md                   # Skill README
│   └── traceability_template.py   # Template script
└── docs/                           # Additional documentation
    ├── SETUP.md                    # Setup guide
    ├── USAGE.md                    # Usage guide
    └── TROUBLESHOOTING.md          # Troubleshooting guide
```

## 🔐 Security & Credentials

### Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Give it a name and copy the token
4. Use it in the configuration

### Azure DevOps PAT
1. Go to your Azure DevOps organization
2. Click User Settings → Personal access tokens
3. Create a new token with "Work Items (Read)" permission
4. Copy and use in configuration

**Security Notes:**
- Never commit credentials to version control
- Use environment variables for production
- Rotate tokens regularly
- Limit PAT permissions to minimum required

## 🛠️ Customization

### Adjust Fuzzy Matching Threshold

```python
# Line 231: Change minimum score
if score >= 60 and ado_id_key:  # Lower from 70 to 60
```

### Change ADO Scan Window

```python
# Line 171: Adjust time period
"[System.CreatedDate] >= @Today - 90"  # Change from 90 days
```

### Increase Match Suggestions

```python
# Line 219: Get more suggestions per item
matches = process.extract(..., limit=10)  # From 5 to 10
```

## 📈 Use Cases

- **UAT Testing** - Track testing issues across both systems
- **Sprint Planning** - Understand work item distribution
- **Compliance Audits** - Generate traceability documentation
- **Status Synchronization** - Identify sync issues between tools
- **Severity Validation** - Ensure consistent priorities
- **Team Coordination** - Monitor assignee alignment
- **Migration Planning** - Assess linkage before migration

## 🐛 Troubleshooting

### "Permission Denied" Error
- Close Excel if the report file is open
- Check file permissions in the output directory

### "Could not connect to Jira"
- Verify API token is valid
- Check Jira URL format
- Ensure project key exists

### "Failed to fetch ADO work item"
- Confirm PAT has read permissions
- Verify TFS server is accessible
- Check network connectivity

### No Fuzzy Matches Found
- Try lowering the threshold (min 60)
- Check if ADO work items exist in the time window
- Verify title similarity is sufficient

## 📝 Requirements

### Python Packages
```
pandas>=2.0.0
openpyxl>=3.1.0
requests>=2.31.0
fuzzywuzzy>=0.18.0
python-Levenshtein>=0.21.0
```

### System Requirements
- Python 3.8 or higher
- 100MB free disk space
- Internet connectivity to Jira and ADO
- Windows, macOS, or Linux

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Created for enterprise Jira-ADO integration and traceability reporting.

## 🙏 Acknowledgments

- Built with Claude Code
- Uses fuzzywuzzy for text matching
- Powered by Jira REST API and Azure DevOps REST API

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
- Review the [FAQ](docs/FAQ.md)

## 🔄 Version History

### v1.0.0 (Current)
- Initial release
- Full Jira-ADO traceability
- Fuzzy matching for unlinked items
- 7-sheet Excel report
- Claude Code skill integration
- Configurable thresholds

---

**⭐ If this tool helps you, please consider starring the repository!**
