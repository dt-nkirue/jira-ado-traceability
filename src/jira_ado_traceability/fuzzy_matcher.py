"""Fuzzy matching for finding potential Jira-ADO links."""

from __future__ import annotations

from typing import Any

import pandas as pd
from fuzzywuzzy import fuzz, process

from jira_ado_traceability.models import FuzzyMatch


def get_confidence_level(score: int) -> str:
    """Determine confidence level based on match score.

    Args:
        score: Match score (0-100)

    Returns:
        Confidence level string
    """
    if score >= 90:
        return "Very High"
    if score >= 80:
        return "High"
    return "Medium"


def _process_jira_row_matches(
    jira_row: pd.Series[Any],
    ado_titles: dict[str, str],
    ado_work_items: list[dict[str, Any]],
    threshold: int,
    limit: int,
) -> list[FuzzyMatch]:
    """Process fuzzy matches for a single Jira row.

    Args:
        jira_row: Single Jira issue row
        ado_titles: Dictionary of ADO IDs to titles
        ado_work_items: List of ADO work items
        threshold: Minimum match score
        limit: Maximum matches per issue

    Returns:
        List of fuzzy matches for this Jira issue
    """
    jira_summary = str(jira_row["Jira Summary"])
    # fuzzywuzzy returns list of tuples: (match_str, score) or (match_str, score, index)
    # Type ignore needed due to fuzzywuzzy incomplete type stubs
    matches = process.extract(jira_summary, ado_titles, scorer=fuzz.token_sort_ratio, limit=limit)  # type: ignore[assignment]
    fuzzy_matches: list[FuzzyMatch] = []

    for match in matches:
        # Extract title and score from tuple (fuzzywuzzy returns variable-length tuples)
        ado_title: str = str(match[0])
        score: int = int(match[1])
        ado_id = _find_ado_id_by_title(ado_titles, ado_title)

        if score >= threshold and ado_id:
            work_item = _find_work_item_by_id(ado_work_items, ado_id)
            if work_item:
                fuzzy_matches.append(
                    FuzzyMatch(
                        jira_key=str(jira_row["Jira Key"]),
                        jira_summary=jira_summary,
                        jira_status=str(jira_row["Jira Status"]),
                        potential_ado_id=ado_id,
                        ado_title=ado_title,
                        ado_state=str(work_item["state"]),
                        ado_work_item_type=str(work_item["work_item_type"]),
                        match_score=score,
                        confidence=get_confidence_level(score),
                    )
                )

    return fuzzy_matches


def find_fuzzy_matches(
    unlinked_jira_df: pd.DataFrame,
    ado_work_items: list[dict[str, Any]],
    threshold: int = 70,
    limit: int = 5,
) -> list[FuzzyMatch]:
    """Find potential matches between unlinked Jira issues and ADO work items.

    Args:
        unlinked_jira_df: DataFrame of Jira issues without ADO links
        ado_work_items: List of ADO work items to match against
        threshold: Minimum match score (0-100)
        limit: Maximum number of matches per Jira issue

    Returns:
        List of fuzzy matches
    """
    if len(ado_work_items) == 0 or len(unlinked_jira_df) == 0:
        return []

    ado_titles = {item["id"]: item["title"] for item in ado_work_items}
    fuzzy_matches: list[FuzzyMatch] = []

    print(f"\nAnalyzing {len(unlinked_jira_df)} unlinked Jira items for potential matches...")

    for _, jira_row in unlinked_jira_df.iterrows():
        row_matches = _process_jira_row_matches(jira_row, ado_titles, ado_work_items, threshold, limit)
        fuzzy_matches.extend(row_matches)

    print(f"Found {len(fuzzy_matches)} potential matches based on title similarity")
    return fuzzy_matches


def _find_ado_id_by_title(ado_titles: dict[str, str], title: str) -> str | None:
    """Find ADO ID by title.

    Args:
        ado_titles: Dictionary mapping ADO IDs to titles
        title: Title to search for

    Returns:
        ADO ID or None
    """
    for ado_id, ado_title in ado_titles.items():
        if ado_title == title:
            return ado_id
    return None


def _find_work_item_by_id(work_items: list[dict[str, Any]], work_item_id: str) -> dict[str, Any] | None:
    """Find work item by ID.

    Args:
        work_items: List of work items
        work_item_id: Work item ID to find

    Returns:
        Work item dictionary or None
    """
    for item in work_items:
        if item["id"] == work_item_id:
            return item
    return None
