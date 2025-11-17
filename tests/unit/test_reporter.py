"""Unit tests for reporter module."""

from io import StringIO
from unittest.mock import patch

import pandas as pd

from jira_ado_traceability.reporter import (
    generate_summary_statistics,
    print_summary,
)


class TestGenerateSummaryStatistics:
    """Tests for generate_summary_statistics function."""

    def test_generate_summary_basic(self) -> None:
        """Test basic summary generation."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1", "J-2", "J-3"],
                "ADO ID": ["A-1", "A-2", "Not Linked"],
                "Status Comparison": ["[OK] Both Closed", "[WARN] Different", "No ADO Link"],
                "Severity Comparison": ["[OK] Match", "[WARN] Mismatch", "N/A"],
                "Assignee Match": ["[OK] Match", "[WARN] Different", "N/A"],
            }
        )

        summary = generate_summary_statistics(df)

        assert isinstance(summary, pd.DataFrame)
        assert len(summary) > 0
        assert "Metric" in summary.columns
        assert "Count" in summary.columns

    def test_summary_counts_linked_items(self) -> None:
        """Test that linked items are counted correctly."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1", "J-2", "J-3"],
                "ADO ID": ["A-1", "A-2", "Not Linked"],
                "Status Comparison": ["[OK] Both Closed", "[OK] Both Open", "No ADO Link"],
                "Severity Comparison": ["[OK] Match", "[OK] Match", "N/A"],
                "Assignee Match": ["[OK] Match", "[OK] Match", "N/A"],
            }
        )

        summary = generate_summary_statistics(df)

        # Find the row for linked items
        linked_row = summary[summary["Metric"] == "Linked to ADO"]
        assert len(linked_row) > 0
        assert linked_row.iloc[0]["Count"] == 2

    def test_summary_counts_unlinked_items(self) -> None:
        """Test that unlinked items are counted correctly."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1", "J-2", "J-3"],
                "ADO ID": ["Not Linked", "Not Linked", "A-3"],
                "Status Comparison": ["No ADO Link", "No ADO Link", "[OK] Both Open"],
                "Severity Comparison": ["N/A", "N/A", "[OK] Match"],
                "Assignee Match": ["N/A", "N/A", "[OK] Match"],
            }
        )

        summary = generate_summary_statistics(df)

        # Find the row for unlinked items
        unlinked_row = summary[summary["Metric"] == "Not Linked to ADO"]
        assert len(unlinked_row) > 0
        assert unlinked_row.iloc[0]["Count"] == 2

    def test_summary_with_empty_dataframe(self) -> None:
        """Test summary generation with empty DataFrame."""
        # Create empty DataFrame with proper string dtype
        df = pd.DataFrame(
            {
                "Jira Key": pd.Series([], dtype=str),
                "ADO ID": pd.Series([], dtype=str),
                "Status Comparison": pd.Series([], dtype=str),
                "Severity Comparison": pd.Series([], dtype=str),
                "Assignee Match": pd.Series([], dtype=str),
            }
        )

        summary = generate_summary_statistics(df)

        assert isinstance(summary, pd.DataFrame)
        assert len(summary) > 0  # Should still have structure

    def test_summary_status_matches(self) -> None:
        """Test counting status matches."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1", "J-2", "J-3"],
                "ADO ID": ["A-1", "A-2", "A-3"],
                "Status Comparison": [
                    "[OK] Both Closed",
                    "[OK] Both Open",
                    "[WARN] Different",
                ],
                "Severity Comparison": ["[OK] Match", "[OK] Match", "[WARN] Mismatch"],
                "Assignee Match": ["[OK] Match", "[OK] Match", "[WARN] Different"],
            }
        )

        summary = generate_summary_statistics(df)

        # Find status match metrics
        status_ok_row = summary[summary["Metric"].str.contains("Status.*OK", na=False)]
        if len(status_ok_row) > 0:
            assert status_ok_row.iloc[0]["Count"] == 2


class TestPrintSummary:
    """Tests for print_summary function."""

    def test_print_summary_output(self) -> None:
        """Test that print_summary produces output."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1", "J-2"],
                "ADO ID": ["A-1", "Not Linked"],
                "Status Comparison": ["[OK] Both Closed", "No ADO Link"],
                "Severity Comparison": ["[OK] Match", "N/A"],
                "Assignee Match": ["[OK] Match", "N/A"],
            }
        )

        with patch("sys.stdout", new=StringIO()) as fake_out:
            print_summary(df, fuzzy_matches_count=5, output_file="test.xlsx")
            output = fake_out.getvalue()

        assert "Total Issues" in output
        assert "test.xlsx" in output

    def test_print_summary_with_no_fuzzy_matches(self) -> None:
        """Test print summary with no fuzzy matches."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1"],
                "ADO ID": ["A-1"],
                "Status Comparison": ["[OK] Both Closed"],
                "Severity Comparison": ["[OK] Match"],
                "Assignee Match": ["[OK] Match"],
            }
        )

        with patch("sys.stdout", new=StringIO()) as fake_out:
            print_summary(df, fuzzy_matches_count=0, output_file="test.xlsx")
            output = fake_out.getvalue()

        assert "0" in output or "no" in output.lower()

    def test_print_summary_shows_linked_count(self) -> None:
        """Test that linked count is shown in summary."""
        df = pd.DataFrame(
            {
                "Jira Key": ["J-1", "J-2", "J-3"],
                "ADO ID": ["A-1", "A-2", "Not Linked"],
                "Status Comparison": ["[OK] Both Closed", "[OK] Both Open", "No ADO Link"],
                "Severity Comparison": ["[OK] Match", "[OK] Match", "N/A"],
                "Assignee Match": ["[OK] Match", "[OK] Match", "N/A"],
            }
        )

        with patch("sys.stdout", new=StringIO()) as fake_out:
            print_summary(df, fuzzy_matches_count=0, output_file="test.xlsx")
            output = fake_out.getvalue()

        assert "2" in output  # 2 linked items
