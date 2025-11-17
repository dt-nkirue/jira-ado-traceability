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


def _get_ado_field_mapping() -> dict[str, str]:
    """Get mapping of DataFrame columns to ADO work item fields.

    Returns:
        Dictionary mapping DataFrame column names to work item field names
    """
    return {
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


def _populate_ado_data(df: pd.DataFrame, ado_work_items: dict[str, AdoWorkItem]) -> pd.DataFrame:
    """Populate ADO data columns in DataFrame.

    Args:
        df: DataFrame to populate
        ado_work_items: Dictionary of ADO work items

    Returns:
        DataFrame with ADO data populated
    """
    ado_field_mapping = _get_ado_field_mapping()

    for col in ado_field_mapping:
        df[col] = ""

    for idx, row in df.iterrows():
        ado_id = str(row["ADO ID"])
        if ado_id in ado_work_items:
            work_item = ado_work_items[ado_id]
            for col, field in ado_field_mapping.items():
                # Get field value from TypedDict with proper typing
                field_value: str = work_item.get(field, "")  # type: ignore[misc]
                df.loc[idx, col] = field_value  # type: ignore[call-overload]

    return df


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
    df = _populate_ado_data(df, ado_work_items)

    df["Status Comparison"] = df.apply(
        lambda row: compare_status(str(row["Jira Status Category"]), str(row["ADO State"])), axis=1
    )
    df["Severity Comparison"] = df.apply(
        lambda row: compare_severity(str(row["Jira Severity"]), str(row["ADO Severity"])), axis=1
    )
    df["Assignee Match"] = df.apply(
        lambda row: compare_assignee(str(row["Jira Assignee"]), str(row["ADO Assigned To"])), axis=1
    )

    return df
