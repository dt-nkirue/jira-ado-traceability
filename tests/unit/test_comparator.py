"""Unit tests for comparator module."""

import pytest

from jira_ado_traceability.comparator import compare_assignee, compare_severity, compare_status


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
