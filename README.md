# Jira-ADO Traceability System

A comprehensive Python tool for generating traceability reports between Jira issues and Azure DevOps (TFS) work items with intelligent fuzzy matching for unlinked items.

## Features

- **Modular Architecture** - Clean, maintainable code structure with strict quality standards
- **Type-Safe** - Full type hints with strict type checking using Pyright
- **Automated Testing** - Comprehensive test suite with unit, integration, and e2e tests
- **Code Quality** - Ruff linting, formatting, and complexity checks
- **Build Automation** - Just-based build system for streamlined development
- **Secure Configuration** - Environment variable support for credentials
- **Detailed Logging** - Comprehensive output for monitoring and troubleshooting
- **Dual Data Sources** - Real-time API fetching (recommended) or static JSON file input
- **Comprehensive Comparison** - Analyzes status, severity, and assignee alignment
- **Fuzzy Matching** - Intelligent title-based matching for unlinked items (70% confidence)
- **Excel Report Generation** - Creates detailed 7-sheet Excel reports with analytics

## Report Sheets

The tool generates an Excel file with 7 comprehensive sheets:

1. **Summary** - High-level statistics and key metrics
2. **Full Traceability** - Complete mapping of all Jira issues to ADO work items
3. **Matched Items** - All Jira issues successfully linked to ADO
4. **Mismatches** - Items with status, severity, or assignee discrepancies
5. **Matched Summary** - Detailed analytics for linked items
6. **Potential Matches** - Fuzzy-matched suggestions for unlinked items
7. **Unlinked Issues** - Jira items without ADO connections

## Quick Start

### Prerequisites

**Required:**
- [uv](https://github.com/astral-sh/uv) - Package and Python manager (auto-installs Python 3.13+)
- [just](https://github.com/casey/just) - Command runner

**Credentials:**
- Jira Cloud account with API access
- Azure DevOps/TFS server access

### Installation

```bash
# Clone the repository
git clone https://github.com/dt-nkirue/jira-ado-traceability.git
cd jira-ado-traceability

# Setup development environment (installs dependencies)
just dev-setup
```

### Configuration

The tool supports two modes: **API Mode** (real-time data fetching) and **File Mode** (static JSON data).

#### Option 1: API Mode (Recommended - Real-time Data)

**Step 1:** Copy the example environment file:

```bash
# Linux/Mac
cp .env.example .env

# Windows (PowerShell)
Copy-Item .env.example .env
```

**Step 2:** Edit `.env` and fill in your credentials:

```bash
# Jira Configuration
JIRA_URL=https://your-company.atlassian.net
JIRA_USERNAME=your.email@company.com
JIRA_API_TOKEN=your-jira-api-token-here
JIRA_PROJECT_KEY=YOUR_PROJECT
JIRA_JQL=project = YOUR_PROJECT AND resolution = Unresolved

# Azure DevOps Configuration
ADO_SERVER=http://tfsserver:8080/tfs
ADO_COLLECTION=YourCollection
ADO_PROJECT=YourProject
ADO_PAT=your-ado-personal-access-token

# Data Source Mode
DATA_SOURCE=API

# Output
OUTPUT_FILE=reports/Jira_ADO_Traceability_Report.xlsx
```

**Note:** The `.env` file is automatically loaded by the tool. You don't need to manually export environment variables.

#### Option 2: File Mode (For Testing with Static Data)

**Step 1:** Copy the example config file:

```bash
# Linux/Mac
cp config.example.json config.json

# Windows (PowerShell)
Copy-Item config.example.json config.json
```

**Step 2:** Edit `config.json` and configure your settings:

```json
{
  "ado_server": "http://tfsserver:8080/tfs",
  "ado_collection": "YourCollection",
  "ado_project": "YourProject",
  "jira_data_file": "path/to/jira_data.json",
  "output_file": "reports/Jira_ADO_Traceability_Report.xlsx",
  "fuzzy_match_threshold": 70,
  "fuzzy_match_limit": 5,
  "ado_scan_days": 90,
  "data_source": "FILE"
}
```

**Step 3:** Set your ADO PAT as an environment variable (or add it to the config):

```bash
# Windows (PowerShell)
$env:ADO_PAT = "your-ado-personal-access-token"

# Linux/Mac
export ADO_PAT="your-ado-personal-access-token"
```

**Note:** Credentials in `config.json` can be overridden by environment variables for better security.

### Usage

```bash
# API Mode - Real-time data fetching (recommended)
# Requires environment variables set as shown above
just run-manual

# File Mode - Using config.json + static Jira JSON
just run-scheduled

# Custom config file
just run-config path/to/config.json
```

**Note:** `run-manual` uses environment variables (API mode), while `run-scheduled` uses a config.json file (FILE mode).

## Development Commands

```bash
# Development workflow
just dev-setup      # Setup environment (first time only)
just format         # Format code with ruff
just check          # Run all quality checks (use after changes!)

# Code quality
just lint           # Linting with ruff
just typecheck      # Type checking with pyright
just fix            # Auto-fix linting issues
just check-noqa     # Ensure no noqa comments
just check-cloc     # Check file line counts

# Testing
just test           # Run all tests (67 unit tests)
just test-cov       # Run tests with coverage report
just test-unit      # Run unit tests

# Build
just build          # Build distribution packages
just clean          # Clean build artifacts
```

## Project Structure

```
jira-ado-traceability-project/
├── src/jira_ado_traceability/   # Source code
│   ├── __init__.py
│   ├── models.py                # Data models and types
│   ├── config.py                # Configuration management
│   ├── jira_parser.py           # Jira JSON parsing
│   ├── jira_client.py           # Jira API client
│   ├── ado_client.py            # ADO API client
│   ├── fuzzy_matcher.py         # Fuzzy matching logic
│   ├── comparator.py            # Comparison functions
│   ├── reporter.py              # Summary statistics
│   ├── excel_generator.py       # Excel report generation
│   ├── cli_manual.py            # Manual mode entry point
│   └── cli_scheduled.py         # Scheduled mode entry point
├── tests/                       # Test suite (67 unit tests)
│   ├── unit/                    # Unit tests (all current tests)
│   ├── integration/             # Integration tests (placeholder)
│   └── e2e/                     # End-to-end tests (placeholder)
├── scripts/                     # Utility scripts
│   └── check_line_counts.py    # Line count validator
├── pyproject.toml              # Project configuration
├── justfile                    # Build automation
├── .pre-commit-config.yaml     # Pre-commit hooks
├── CLAUDE.md                   # AI assistant guidelines
└── README.md                   # This file
```

## Code Quality Standards

This project follows strict code quality standards:

- **Maximum file length**: 500 lines
- **Maximum function complexity**: 10
- **Type checking**: Strict mode with Pyright
- **Linting**: Ruff with comprehensive rule set
- **No `noqa` comments**: All issues must be properly resolved
- **Pre-commit hooks**: Security scanning with gitleaks

## Testing

```bash
# Run all tests
just test

# Run with coverage
just test-cov

# Run unit tests
just test-unit
```

**Current Test Suite:** 67 comprehensive unit tests covering:
- Configuration management
- Jira JSON parsing
- ADO API client with mocking
- Fuzzy matching logic
- Comparison functions
- Report generation

All tests passing with strict type checking and quality standards.

## Fuzzy Matching

The tool uses intelligent fuzzy matching to suggest potential links:

- **Algorithm**: Token sort ratio (handles word order differences)
- **Threshold**: 70% minimum similarity (configurable)
- **Confidence Levels**:
  - Very High (90-100%)
  - High (80-89%)
  - Medium (70-79%)
- **Scan Scope**: Configurable days (default: 90 days)
- **Match Limit**: Top N suggestions per Jira item (default: 5)

## Security & Credentials

### Jira API Token
1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click "Create API token"
3. Copy and store securely

### Azure DevOps PAT
1. Go to your Azure DevOps organization
2. Click User Settings → Personal access tokens
3. Create token with "Work Items (Read)" permission
4. Store in environment variable `ADO_PAT`

**Security Best Practices:**
- Never commit credentials to version control
- Use environment variables for production
- Rotate tokens regularly
- Limit PAT permissions to minimum required
- Pre-commit hooks scan for secrets

## Customization

### Adjust Fuzzy Matching Threshold

Edit `config.json`:
```json
{
  "fuzzy_match_threshold": 60
}
```

### Change ADO Scan Window

Edit `config.json`:
```json
{
  "ado_scan_days": 120
}
```

### Increase Match Suggestions

Edit `config.json`:
```json
{
  "fuzzy_match_limit": 10
}
```

## Troubleshooting

### Permission Denied Error
- Close Excel if the report file is open
- Check file permissions in the output directory

### Could not connect to ADO
- Verify PAT has read permissions
- Check TFS server is accessible
- Verify network connectivity

### No Fuzzy Matches Found
- Try lowering the threshold (min 60)
- Check if ADO work items exist in the time window
- Verify title similarity is sufficient

### Quality Check Failures

```bash
# Fix linting issues automatically
just fix

# Format code
just format

# Check what's failing
just check
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run `just format` and `just check` after changes
4. Ensure all tests pass (`just test`)
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Version History

### v1.0.0 (Current)
- Modular architecture with strict quality standards
- Full type hints and type checking
- Comprehensive test suite
- Build automation with just
- Pre-commit hooks with security scanning
- Configuration file support
- Environment variable support

---

Built with modern Python best practices using `uv`, `just`, `ruff`, and `pyright`.
