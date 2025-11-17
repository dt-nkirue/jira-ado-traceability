"""Jira issue parser for extracting and transforming issue data."""

import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_jira_data(file_path: str | Path) -> dict[str, Any]:
    """Load Jira data from JSON file.

    Args:
        file_path: Path to Jira JSON data file

    Returns:
        Dictionary containing Jira data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    data_file = Path(file_path)

    if not data_file.exists():
        msg = f"Jira data file not found: {file_path}"
        raise FileNotFoundError(msg)

    with data_file.open(encoding="utf-8") as f:
        return json.load(f)


def parse_jira_issue(issue: dict[str, Any]) -> dict[str, Any]:
    """Parse a single Jira issue into structured format.

    Args:
        issue: Raw Jira issue dictionary

    Returns:
        Parsed issue data dictionary
    """
    fields = issue.get("fields", {})

    # Basic fields
    jira_key = issue.get("key", "")
    jira_summary = fields.get("summary", "")

    # Status
    status = fields.get("status", {})
    jira_status = status.get("name", "Unknown")
    jira_status_category = status.get("statusCategory", {}).get("name", "Unknown")

    # Priority
    priority = fields.get("priority", {})
    jira_priority = priority.get("name", "None") if priority else "None"

    # Severity (customfield_10042)
    severity = fields.get("customfield_10042", {})
    jira_severity = severity.get("value", "None") if severity else "None"

    # Assignee
    assignee = fields.get("assignee", {})
    jira_assignee = assignee.get("displayName", "Unassigned") if assignee else "Unassigned"

    # Dates
    created = fields.get("created", "")
    jira_created = pd.to_datetime(created, utc=True).tz_localize(None) if created else None

    resolutiondate = fields.get("resolutiondate")
    jira_resolved = pd.to_datetime(resolutiondate, utc=True).tz_localize(None) if resolutiondate else None

    # ADO fields from Jira
    ado_id = fields.get("customfield_10109", "")  # AzureDevOps ID
    ado_state_jira = fields.get("customfield_10110", "")  # AzureDevOps State (from Jira)

    return {
        "Jira Key": jira_key,
        "Jira Summary": jira_summary,
        "Jira Status": jira_status,
        "Jira Status Category": jira_status_category,
        "Jira Priority": jira_priority,
        "Jira Severity": jira_severity,
        "Jira Assignee": jira_assignee,
        "Jira Created": jira_created,
        "Jira Resolved": jira_resolved,
        "ADO ID": ado_id if ado_id else "Not Linked",
        "ADO State (Jira)": ado_state_jira if ado_state_jira else "N/A",
    }


def parse_jira_issues(jira_data: dict[str, Any]) -> pd.DataFrame:
    """Parse all Jira issues from data dictionary.

    Args:
        jira_data: Dictionary containing Jira issues

    Returns:
        DataFrame with parsed Jira issues
    """
    issues = jira_data.get("issues", [])
    parsed_data = [parse_jira_issue(issue) for issue in issues]
    return pd.DataFrame(parsed_data)


def load_and_parse_jira_issues(file_path: str | Path) -> pd.DataFrame:
    """Load Jira data file and parse all issues.

    Args:
        file_path: Path to Jira JSON data file

    Returns:
        DataFrame with parsed Jira issues

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    jira_data = load_jira_data(file_path)
    return parse_jira_issues(jira_data)
