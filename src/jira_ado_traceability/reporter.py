"""Summary statistics and reporting functions."""

import pandas as pd


def generate_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics from traceability DataFrame.

    Args:
        df: Full traceability DataFrame

    Returns:
        DataFrame with summary statistics
    """
    total_issues = len(df)
    linked_issues = len(df[df["ADO ID"] != "Not Linked"])
    unlinked_issues = total_issues - linked_issues

    # Only count mismatches among linked items
    df_linked = df[df["ADO ID"] != "Not Linked"]
    status_mismatches = len(df_linked[df_linked["Status Comparison"].str.contains("[WARN]", na=False)])
    severity_mismatches = len(df_linked[df_linked["Severity Comparison"].str.contains("[WARN]", na=False)])
    assignee_mismatches = len(df_linked[df_linked["Assignee Match"].str.contains("[WARN]", na=False)])

    both_closed = len(df_linked[df_linked["Status Comparison"] == "[OK] Both Closed"])
    both_open = len(df_linked[df_linked["Status Comparison"] == "[OK] Both Open"])

    summary_stats = {
        "Metric": [
            "Total Jira Issues",
            "Linked to ADO",
            "Not Linked to ADO",
            "Both Closed",
            "Both Open",
            "Status Mismatches",
            "Severity Mismatches",
            "Assignee Mismatches",
        ],
        "Count": [
            total_issues,
            linked_issues,
            unlinked_issues,
            both_closed,
            both_open,
            status_mismatches,
            severity_mismatches,
            assignee_mismatches,
        ],
    }

    return pd.DataFrame(summary_stats)


def print_summary(
    df: pd.DataFrame,
    fuzzy_matches_count: int,
    output_file: str,
) -> None:
    """Print summary to console.

    Args:
        df: Full traceability DataFrame
        fuzzy_matches_count: Number of fuzzy matches found
        output_file: Output file path
    """
    total_issues = len(df)
    linked_issues = len(df[df["ADO ID"] != "Not Linked"])
    unlinked_issues = total_issues - linked_issues

    # Only count mismatches among linked items
    df_linked = df[df["ADO ID"] != "Not Linked"]
    status_mismatches = len(df_linked[df_linked["Status Comparison"].str.contains("[WARN]", na=False)])
    severity_mismatches = len(df_linked[df_linked["Severity Comparison"].str.contains("[WARN]", na=False)])
    assignee_mismatches = len(df_linked[df_linked["Assignee Match"].str.contains("[WARN]", na=False)])

    # Calculate perfect matches
    df_matched = df[df["ADO ID"] != "Not Linked"]
    perfect_matches = len(
        df_matched[
            (df_matched["Status Comparison"].str.contains("[OK]", na=False))
            & (df_matched["Severity Comparison"].str.contains("[OK]", na=False))
            & (df_matched["Assignee Match"].str.contains("[OK]", na=False))
        ]
    )

    print(f"\n[SUCCESS] Report generated successfully: {output_file}")
    print("\nSummary:")
    print(f"  Total Issues: {total_issues}")
    print(f"  Linked to ADO: {linked_issues}")
    print(f"  Not Linked: {unlinked_issues}")
    print(f"  Potential Matches Found (Fuzzy): {fuzzy_matches_count}")
    print(f"  Perfect Matches (Status+Severity+Assignee): {perfect_matches}")
    print(f"  Status Mismatches (among linked): {status_mismatches}")
    print(f"  Severity Mismatches (among linked): {severity_mismatches}")
    print(f"  Assignee Mismatches (among linked): {assignee_mismatches}")
