"""Legacy entry point for Jira-ADO traceability (manual mode).

This script provides backward compatibility with the original monolithic version.
It now uses the modular code from src/ package.

Usage:
    python scripts/jira_ado_traceability.py

For the new recommended way, use:
    just run-manual
    or
    uv run python src/jira_ado_traceability/cli_manual.py
"""

import sys
from pathlib import Path

# Add src to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from jira_ado_traceability.ado_client import AdoClient
from jira_ado_traceability.comparator import add_comparison_columns
from jira_ado_traceability.config import create_manual_config
from jira_ado_traceability.excel_generator import generate_excel_report
from jira_ado_traceability.fuzzy_matcher import find_fuzzy_matches
from jira_ado_traceability.jira_parser import load_and_parse_jira_issues
from jira_ado_traceability.reporter import generate_summary_statistics, print_summary


def main() -> None:
    """Run traceability report in manual mode."""
    print("=" * 60)
    print("Jira-ADO Traceability Report Generator (Legacy Mode)")
    print("=" * 60)
    print()

    # Configuration (hardcoded for backward compatibility)
    config = create_manual_config(
        ado_server="http://tfsserver:8080/tfs",
        ado_collection="YourCollection",
        ado_project="YourProject",
        ado_pat="your-ado-personal-access-token",
        jira_data_file=r"C:\Users\nkirue\AI-Playarea\jira_with_ado.json",
        output_file=r"C:\Users\nkirue\AI-Playarea\Jira_ADO_Traceability_Report.xlsx",
    )

    # Load and parse Jira issues
    print("Loading Jira data...")
    df = load_and_parse_jira_issues(config.jira_data_file)
    print(f"Found {len(df)} Jira issues")

    # Fetch ADO work items for linked issues
    print("\nFetching Azure DevOps work items...")
    ado_client = AdoClient(config)
    ado_ids = df[df["ADO ID"] != "Not Linked"]["ADO ID"].unique().tolist()
    print(f"Found {len(ado_ids)} unique ADO work items to fetch")
    ado_work_items = ado_client.fetch_work_items(ado_ids)

    # Perform fuzzy matching for unlinked items
    print("\nPerforming fuzzy matching for unlinked Jira items...")
    print("Fetching all ADO work items for fuzzy matching...")
    all_ado_work_items = ado_client.query_recent_work_items(days=config.ado_scan_days)

    unlinked_df = df[df["ADO ID"] == "Not Linked"]
    fuzzy_matches = find_fuzzy_matches(
        unlinked_df,
        all_ado_work_items,
        threshold=config.fuzzy_match_threshold,
        limit=config.fuzzy_match_limit,
    )

    # Merge ADO data and add comparisons
    print("\nMerging Jira and ADO data...")
    df = add_comparison_columns(df, ado_work_items)

    # Generate summary statistics
    print("\nGenerating summary statistics...")
    summary_df = generate_summary_statistics(df)

    # Generate Excel report
    generate_excel_report(config.output_file, df, summary_df, fuzzy_matches)

    # Print summary
    print_summary(df, len(fuzzy_matches), config.output_file)

    print()
    print("=" * 60)
    print("Report generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        print("\nPlease update the configuration in this script:")
        print(f"  Edit: {__file__}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        sys.exit(1)
