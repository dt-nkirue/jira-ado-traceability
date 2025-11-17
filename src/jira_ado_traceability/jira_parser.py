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


def _parse_jira_dates(fields: dict[str, Any]) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    """Parse date fields from Jira issue.

    Args:
        fields: Jira issue fields dictionary

    Returns:
        Tuple of (created_date, resolved_date)
    """
    created = fields.get("created", "")
    jira_created: pd.Timestamp | None = None
    if created:
        parsed_created = pd.to_datetime(created, utc=True)
        jira_created = parsed_created.tz_localize(None) if hasattr(parsed_created, "tz_localize") else None

    resolutiondate = fields.get("resolutiondate")
    jira_resolved: pd.Timestamp | None = None
    if resolutiondate:
        parsed_resolved = pd.to_datetime(resolutiondate, utc=True)
        jira_resolved = parsed_resolved.tz_localize(None) if hasattr(parsed_resolved, "tz_localize") else None

    return jira_created, jira_resolved


def _extract_jira_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """Extract and parse Jira fields into a structured dictionary.

    Args:
        fields: Jira issue fields dictionary

    Returns:
        Dictionary with extracted field values
    """
    status = fields.get("status", {})
    priority = fields.get("priority", {})
    severity = fields.get("customfield_10042", {})
    assignee = fields.get("assignee", {})

    jira_created, jira_resolved = _parse_jira_dates(fields)

    return {
        "summary": fields.get("summary", ""),
        "status": status.get("name", "Unknown"),
        "status_category": status.get("statusCategory", {}).get("name", "Unknown"),
        "priority": priority.get("name", "None") if priority else "None",
        "severity": severity.get("value", "None") if severity else "None",
        "assignee": assignee.get("displayName", "Unassigned") if assignee else "Unassigned",
        "created": jira_created,
        "resolved": jira_resolved,
        "ado_id": fields.get("customfield_10109", ""),
        "ado_state": fields.get("customfield_10110", ""),
    }


def parse_jira_issue(issue: dict[str, Any]) -> dict[str, Any]:
    """Parse a single Jira issue into structured format.

    Args:
        issue: Raw Jira issue dictionary

    Returns:
        Parsed issue data dictionary
    """
    fields = issue.get("fields", {})
    extracted = _extract_jira_fields(fields)

    return {
        "Jira Key": issue.get("key", ""),
        "Jira Summary": extracted["summary"],
        "Jira Status": extracted["status"],
        "Jira Status Category": extracted["status_category"],
        "Jira Priority": extracted["priority"],
        "Jira Severity": extracted["severity"],
        "Jira Assignee": extracted["assignee"],
        "Jira Created": extracted["created"],
        "Jira Resolved": extracted["resolved"],
        "ADO ID": extracted["ado_id"] if extracted["ado_id"] else "Not Linked",
        "ADO State (Jira)": extracted["ado_state"] if extracted["ado_state"] else "N/A",
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
