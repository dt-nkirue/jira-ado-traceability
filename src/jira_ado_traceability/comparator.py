"""Comparison functions for Jira and ADO data."""

import pandas as pd

from jira_ado_traceability.models import AdoWorkItem


def compare_status(jira_status_category: str, ado_state: str) -> str:
    """Compare status alignment between Jira and ADO.

    Args:
        jira_status_category: Jira status category (e.g., "Done", "In Progress")
        ado_state: ADO state (e.g., "Closed", "Active")

    Returns:
        Comparison result string
    """
    if not ado_state or ado_state == "":
        return "No ADO Link"

    # Normalize states
    jira_done = jira_status_category.lower() == "done"
    ado_closed = ado_state.lower() in ["closed", "resolved", "done", "removed"]

    if jira_done and ado_closed:
        return "[OK] Both Closed"
    if not jira_done and not ado_closed:
        return "[OK] Both Open"
    if jira_done and not ado_closed:
        return "[WARN] Jira Closed, ADO Open"
    return "[WARN] ADO Closed, Jira Open"


def compare_severity(jira_severity: str, ado_severity: str) -> str:
    """Compare severity between systems.

    Args:
        jira_severity: Jira severity value
        ado_severity: ADO severity value

    Returns:
        Comparison result string
    """
    if not ado_severity or ado_severity == "":
        return "N/A"

    # Extract numbers from severity strings (e.g., "Sev-4" -> "4")
    jira_num = "".join(filter(str.isdigit, str(jira_severity)))
    ado_num = str(ado_severity).strip()

    if jira_num == ado_num:
        return "[OK] Match"
    return f"[WARN] Mismatch (J:{jira_severity} vs A:{ado_severity})"


def compare_assignee(jira_assignee: str, ado_assignee: str) -> str:
    """Compare assignee between systems.

    Args:
        jira_assignee: Jira assignee name
        ado_assignee: ADO assignee name

    Returns:
        Comparison result string
    """
    if jira_assignee.lower() == ado_assignee.lower():
        return "[OK] Match"
    return "[WARN] Different"


def add_comparison_columns(
    df: pd.DataFrame,
    ado_work_items: dict[str, AdoWorkItem],
) -> pd.DataFrame:
    """Add ADO data and comparison columns to Jira DataFrame.

    Args:
        df: Jira DataFrame
        ado_work_items: Dictionary of ADO work items

    Returns:
        DataFrame with ADO data and comparison columns added
    """
    # Define ADO columns to add
    ado_field_mapping = {
        "ADO Title": "title",
        "ADO State": "state",
        "ADO Assigned To": "assigned_to",
        "ADO Work Item Type": "work_item_type",
        "ADO Priority": "priority",
        "ADO Severity": "severity",
        "ADO Created Date": "created_date",
        "ADO Closed Date": "closed_date",
        "ADO Resolved Date": "resolved_date",
        "ADO Area Path": "area_path",
        "ADO Iteration Path": "iteration_path",
    }

    # Initialize ADO columns
    for col in ado_field_mapping:
        df[col] = ""

    # Fill in ADO data
    for idx, row in df.iterrows():
        ado_id = str(row["ADO ID"])
        if ado_id in ado_work_items:
            work_item = ado_work_items[ado_id]
            for col, field in ado_field_mapping.items():
                df.at[idx, col] = work_item.get(field, "")

    # Add comparison columns
    df["Status Comparison"] = df.apply(
        lambda row: compare_status(row["Jira Status Category"], row["ADO State"]),
        axis=1,
    )

    df["Severity Comparison"] = df.apply(
        lambda row: compare_severity(row["Jira Severity"], row["ADO Severity"]),
        axis=1,
    )

    df["Assignee Match"] = df.apply(
        lambda row: compare_assignee(row["Jira Assignee"], row["ADO Assigned To"]),
        axis=1,
    )

    return df
