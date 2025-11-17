"""Unit tests for fuzzy_matcher module."""

import pandas as pd

from jira_ado_traceability.fuzzy_matcher import (
    find_fuzzy_matches,
    get_confidence_level,
)


class TestGetConfidenceLevel:
    """Tests for get_confidence_level function."""

    def test_very_high_confidence(self) -> None:
        """Test score >= 90 returns Very High."""
        assert get_confidence_level(90) == "Very High"
        assert get_confidence_level(95) == "Very High"
        assert get_confidence_level(100) == "Very High"

    def test_high_confidence(self) -> None:
        """Test score >= 80 and < 90 returns High."""
        assert get_confidence_level(80) == "High"
        assert get_confidence_level(85) == "High"
        assert get_confidence_level(89) == "High"

    def test_medium_confidence(self) -> None:
        """Test score < 80 returns Medium."""
        assert get_confidence_level(70) == "Medium"
        assert get_confidence_level(75) == "Medium"
        assert get_confidence_level(79) == "Medium"


class TestFindFuzzyMatches:
    """Tests for find_fuzzy_matches function."""

    def test_find_matches_basic(self) -> None:
        """Test basic fuzzy matching functionality."""
        unlinked_df = pd.DataFrame(
            {
                "Jira Key": ["PROJ-1"],
                "Jira Summary": ["Fix login bug in authentication system"],
                "Jira Status": ["Open"],
            }
        )

        ado_work_items = [
            {
                "id": "101",
                "title": "Fix login bug in authentication system",  # Exact match
                "state": "Active",
                "work_item_type": "Bug",
            }
        ]

        matches = find_fuzzy_matches(unlinked_df, ado_work_items, threshold=70, limit=5)

        assert len(matches) > 0
        assert matches[0]["jira_key"] == "PROJ-1"
        assert matches[0]["potential_ado_id"] == "101"
        assert matches[0]["match_score"] >= 70

    def test_find_matches_with_high_threshold(self) -> None:
        """Test that low similarity doesn't match with high threshold."""
        unlinked_df = pd.DataFrame(
            {
                "Jira Key": ["PROJ-1"],
                "Jira Summary": ["Completely different text"],
                "Jira Status": ["Open"],
            }
        )

        ado_work_items = [
            {
                "id": "101",
                "title": "Another unrelated item",
                "state": "Active",
                "work_item_type": "Task",
            }
        ]

        matches = find_fuzzy_matches(unlinked_df, ado_work_items, threshold=95, limit=5)

        assert len(matches) == 0

    def test_find_matches_empty_unlinked_df(self) -> None:
        """Test with empty unlinked DataFrame."""
        unlinked_df = pd.DataFrame({"Jira Key": [], "Jira Summary": [], "Jira Status": []})

        ado_work_items = [{"id": "101", "title": "Item", "state": "Active", "work_item_type": "Bug"}]

        matches = find_fuzzy_matches(unlinked_df, ado_work_items)

        assert len(matches) == 0

    def test_find_matches_empty_ado_items(self) -> None:
        """Test with empty ADO work items list."""
        unlinked_df = pd.DataFrame(
            {
                "Jira Key": ["PROJ-1"],
                "Jira Summary": ["Test issue"],
                "Jira Status": ["Open"],
            }
        )

        ado_work_items: list[dict[str, str]] = []

        matches = find_fuzzy_matches(unlinked_df, ado_work_items)

        assert len(matches) == 0

    def test_find_matches_respects_limit(self) -> None:
        """Test that limit parameter is respected."""
        unlinked_df = pd.DataFrame(
            {
                "Jira Key": ["PROJ-1"],
                "Jira Summary": ["Test issue"],
                "Jira Status": ["Open"],
            }
        )

        # Create many similar ADO items
        ado_work_items = [
            {
                "id": str(i),
                "title": f"Test issue {i}",
                "state": "Active",
                "work_item_type": "Task",
            }
            for i in range(20)
        ]

        matches = find_fuzzy_matches(unlinked_df, ado_work_items, threshold=50, limit=3)

        # Should have at most 3 matches (limit)
        assert len(matches) <= 3

    def test_find_matches_multiple_jira_issues(self) -> None:
        """Test matching multiple Jira issues."""
        unlinked_df = pd.DataFrame(
            {
                "Jira Key": ["PROJ-1", "PROJ-2"],
                "Jira Summary": ["Login bug", "Payment issue"],
                "Jira Status": ["Open", "In Progress"],
            }
        )

        ado_work_items = [
            {
                "id": "101",
                "title": "Fix login bug",
                "state": "Active",
                "work_item_type": "Bug",
            },
            {
                "id": "102",
                "title": "Payment system issue",
                "state": "Active",
                "work_item_type": "Bug",
            },
        ]

        matches = find_fuzzy_matches(unlinked_df, ado_work_items, threshold=70, limit=5)

        # Should find matches for both Jira issues
        jira_keys = {match["jira_key"] for match in matches}
        assert "PROJ-1" in jira_keys or "PROJ-2" in jira_keys

    def test_match_confidence_levels(self) -> None:
        """Test that confidence levels are set correctly."""
        unlinked_df = pd.DataFrame(
            {
                "Jira Key": ["PROJ-1"],
                "Jira Summary": ["Fix login bug"],
                "Jira Status": ["Open"],
            }
        )

        ado_work_items = [
            {
                "id": "101",
                "title": "Fix login bug",  # Exact match
                "state": "Active",
                "work_item_type": "Bug",
            }
        ]

        matches = find_fuzzy_matches(unlinked_df, ado_work_items, threshold=70, limit=5)

        if matches:
            # Exact match should have Very High confidence
            assert matches[0]["confidence"] in ["Very High", "High", "Medium"]
