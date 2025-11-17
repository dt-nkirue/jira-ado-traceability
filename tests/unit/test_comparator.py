"""Unit tests for comparator module."""

import pandas as pd

from jira_ado_traceability.comparator import (
    add_comparison_columns,
    compare_assignee,
    compare_severity,
    compare_status,
)
from jira_ado_traceability.models import AdoWorkItem


def test_compare_status_both_closed():
    result = compare_status("Done", "Closed")
    assert result == "[OK] Both Closed"


def test_compare_status_both_open():
    result = compare_status("In Progress", "Active")
    assert result == "[OK] Both Open"


def test_compare_status_jira_closed_ado_open():
    result = compare_status("Done", "Active")
    assert result == "[WARN] Jira Closed, ADO Open"


def test_compare_status_ado_closed_jira_open():
    result = compare_status("In Progress", "Closed")
    assert result == "[WARN] ADO Closed, Jira Open"


def test_compare_status_no_ado_link():
    result = compare_status("Done", "")
    assert result == "No ADO Link"


def test_compare_severity_match():
    result = compare_severity("Sev-3", "3")
    assert result == "[OK] Match"


def test_compare_severity_mismatch():
    result = compare_severity("Sev-2", "3")
    assert result == "[WARN] Mismatch (J:Sev-2 vs A:3)"


def test_compare_severity_no_ado():
    result = compare_severity("Sev-3", "")
    assert result == "N/A"


def test_compare_assignee_match():
    result = compare_assignee("John Doe", "John Doe")
    assert result == "[OK] Match"


def test_compare_assignee_case_insensitive():
    result = compare_assignee("John Doe", "john doe")
    assert result == "[OK] Match"


def test_compare_assignee_different():
    result = compare_assignee("John Doe", "Jane Smith")
    assert result == "[WARN] Different"


class TestAddComparisonColumns:
    """Tests for add_comparison_columns function."""

    def test_add_comparison_columns_basic(self) -> None:
        """Test adding comparison columns to DataFrame."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1"],
                "ADO ID": ["A-1"],
                "Jira Status Category": ["Done"],
                "Jira Severity": ["Sev-2"],
                "Jira Assignee": ["John Doe"],
            }
        )

        ado_work_items = {
            "A-1": AdoWorkItem(
                id="A-1",
                title="Test Item",
                state="Closed",
                assigned_to="John Doe",
                work_item_type="Bug",
                priority="2",
                severity="2",
                created_date="2024-01-01",
                closed_date="2024-01-10",
                resolved_date="2024-01-10",
                area_path="Area",
                iteration_path="Iteration",
            )
        }

        result = add_comparison_columns(df, ado_work_items)

        assert "ADO State" in result.columns
        assert "ADO Severity" in result.columns
        assert "Status Comparison" in result.columns
        assert "Severity Comparison" in result.columns
        assert "Assignee Match" in result.columns
        assert result.iloc[0]["ADO State"] == "Closed"

    def test_add_comparison_columns_unlinked(self) -> None:
        """Test with unlinked Jira items."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1"],
                "ADO ID": ["Not Linked"],
                "Jira Status Category": ["Done"],
                "Jira Severity": ["Sev-2"],
                "Jira Assignee": ["John Doe"],
            }
        )

        ado_work_items: dict[str, AdoWorkItem] = {}

        result = add_comparison_columns(df, ado_work_items)

        assert "Status Comparison" in result.columns
        assert result.iloc[0]["Status Comparison"] == "No ADO Link"

    def test_add_comparison_columns_multiple_items(self) -> None:
        """Test with multiple Jira items."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1", "J-2"],
                "ADO ID": ["A-1", "Not Linked"],
                "Jira Status Category": ["Done", "In Progress"],
                "Jira Severity": ["Sev-1", "Sev-2"],
                "Jira Assignee": ["John", "Jane"],
            }
        )

        ado_work_items = {
            "A-1": AdoWorkItem(
                id="A-1",
                title="Item 1",
                state="Closed",
                assigned_to="John",
                work_item_type="Bug",
                priority="1",
                severity="1",
                created_date="2024-01-01",
                closed_date="2024-01-10",
                resolved_date="2024-01-10",
                area_path="Area",
                iteration_path="Iteration",
            )
        }

        result = add_comparison_columns(df, ado_work_items)

        assert len(result) == 2
        assert result.iloc[0]["ADO State"] == "Closed"
        assert result.iloc[1]["ADO State"] == ""  # Unlinked
