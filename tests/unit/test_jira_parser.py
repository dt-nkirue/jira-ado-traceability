"""Unit tests for jira_parser module."""

import json
from pathlib import Path

import pandas as pd
import pytest

from jira_ado_traceability.jira_parser import (
    load_and_parse_jira_issues,
    load_jira_data,
    parse_jira_issue,
    parse_jira_issues,
)


class TestLoadJiraData:
    """Tests for load_jira_data function."""

    def test_load_valid_json(self, tmp_path: Path) -> None:
        """Test loading valid JSON file."""
        test_file = tmp_path / "test.json"
        test_data = {"issues": [{"key": "TEST-1", "fields": {}}]}
        test_file.write_text(json.dumps(test_data))

        result = load_jira_data(test_file)

        assert result == test_data
        assert "issues" in result

    def test_load_nonexistent_file(self) -> None:
        """Test loading non-existent file raises error."""
        with pytest.raises(FileNotFoundError, match="Jira data file not found"):
            load_jira_data("nonexistent.json")

    def test_load_invalid_json(self, tmp_path: Path) -> None:
        """Test loading invalid JSON raises error."""
        test_file = tmp_path / "invalid.json"
        test_file.write_text("not valid json {")

        with pytest.raises(json.JSONDecodeError):
            load_jira_data(test_file)


class TestParseJiraIssue:
    """Tests for parse_jira_issue function."""

    def test_parse_complete_issue(self) -> None:
        """Test parsing issue with all fields."""
        issue = {
            "key": "PROJ-123",
            "fields": {
                "summary": "Test Issue",
                "status": {"name": "In Progress", "statusCategory": {"name": "In Progress"}},
                "priority": {"name": "High"},
                "customfield_10042": {"value": "Sev-2"},
                "assignee": {"displayName": "John Doe"},
                "created": "2024-01-15T10:00:00.000+0000",
                "resolutiondate": "2024-01-20T15:30:00.000+0000",
                "customfield_10109": "12345",
                "customfield_10110": "Active",
            },
        }

        result = parse_jira_issue(issue)

        assert result["Jira Key"] == "PROJ-123"
        assert result["Jira Summary"] == "Test Issue"
        assert result["Jira Status"] == "In Progress"
        assert result["Jira Status Category"] == "In Progress"
        assert result["Jira Priority"] == "High"
        assert result["Jira Severity"] == "Sev-2"
        assert result["Jira Assignee"] == "John Doe"
        assert result["ADO ID"] == "12345"
        assert result["ADO State (Jira)"] == "Active"

    def test_parse_issue_with_missing_fields(self) -> None:
        """Test parsing issue with missing optional fields."""
        issue = {
            "key": "PROJ-456",
            "fields": {
                "summary": "Minimal Issue",
                "status": {"name": "Open"},
            },
        }

        result = parse_jira_issue(issue)

        assert result["Jira Key"] == "PROJ-456"
        assert result["Jira Summary"] == "Minimal Issue"
        assert result["Jira Priority"] == "None"
        assert result["Jira Severity"] == "None"
        assert result["Jira Assignee"] == "Unassigned"
        assert result["ADO ID"] == "Not Linked"
        assert result["ADO State (Jira)"] == "N/A"

    def test_parse_issue_without_assignee(self) -> None:
        """Test parsing issue with no assignee."""
        issue = {
            "key": "PROJ-789",
            "fields": {
                "summary": "Unassigned Issue",
                "status": {"name": "Open"},
                "assignee": None,
            },
        }

        result = parse_jira_issue(issue)

        assert result["Jira Assignee"] == "Unassigned"

    def test_parse_issue_without_priority(self) -> None:
        """Test parsing issue with no priority."""
        issue = {
            "key": "PROJ-101",
            "fields": {
                "summary": "No Priority",
                "status": {"name": "Open"},
                "priority": None,
            },
        }

        result = parse_jira_issue(issue)

        assert result["Jira Priority"] == "None"

    def test_parse_issue_without_severity(self) -> None:
        """Test parsing issue with no severity."""
        issue = {
            "key": "PROJ-102",
            "fields": {
                "summary": "No Severity",
                "status": {"name": "Open"},
                "customfield_10042": None,
            },
        }

        result = parse_jira_issue(issue)

        assert result["Jira Severity"] == "None"


class TestParseJiraIssues:
    """Tests for parse_jira_issues function."""

    def test_parse_multiple_issues(self) -> None:
        """Test parsing multiple issues into DataFrame."""
        jira_data = {
            "issues": [
                {
                    "key": "PROJ-1",
                    "fields": {
                        "summary": "Issue 1",
                        "status": {"name": "Open"},
                    },
                },
                {
                    "key": "PROJ-2",
                    "fields": {
                        "summary": "Issue 2",
                        "status": {"name": "Closed"},
                    },
                },
            ]
        }

        df = parse_jira_issues(jira_data)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert df.iloc[0]["Jira Key"] == "PROJ-1"
        assert df.iloc[1]["Jira Key"] == "PROJ-2"

    def test_parse_empty_issues(self) -> None:
        """Test parsing empty issues list."""
        jira_data = {"issues": []}

        df = parse_jira_issues(jira_data)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0


class TestLoadAndParseJiraIssues:
    """Tests for load_and_parse_jira_issues function."""

    def test_load_and_parse_integration(self, tmp_path: Path) -> None:
        """Test complete load and parse workflow."""
        test_file = tmp_path / "jira.json"
        jira_data = {
            "issues": [
                {
                    "key": "TEST-1",
                    "fields": {
                        "summary": "Test Issue",
                        "status": {"name": "Open"},
                        "priority": {"name": "Medium"},
                    },
                }
            ]
        }
        test_file.write_text(json.dumps(jira_data))

        df = load_and_parse_jira_issues(test_file)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 1
        assert df.iloc[0]["Jira Key"] == "TEST-1"
        assert df.iloc[0]["Jira Summary"] == "Test Issue"
        assert df.iloc[0]["Jira Priority"] == "Medium"
