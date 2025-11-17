"""CLI entry point for scheduled mode (config file based)."""

import argparse
import sys
from pathlib import Path

from jira_ado_traceability.ado_client import AdoClient
from jira_ado_traceability.comparator import add_comparison_columns
from jira_ado_traceability.config import load_config_from_file
from jira_ado_traceability.excel_generator import generate_excel_report
from jira_ado_traceability.fuzzy_matcher import find_fuzzy_matches
from jira_ado_traceability.jira_parser import load_and_parse_jira_issues
from jira_ado_traceability.reporter import generate_summary_statistics, print_summary


def parse_args() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Generate Jira-ADO traceability report (scheduled mode)")
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration JSON file (default: config.json)",
    )
    return parser.parse_args()


def main() -> int:
    """Run traceability report in scheduled mode.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        # Parse arguments
        args = parse_args()

        # Load configuration
        print(f"Loading configuration from {args.config}...")
        config = load_config_from_file(args.config)

        # Resolve file paths
        if config.jira_data_file:
            jira_file = Path(config.jira_data_file)
        else:
            print("ERROR: jira_data_file not specified in config")
            return 1

        if config.output_file:
            output_file = Path(config.output_file)
        else:
            output_file = Path("Jira_ADO_Traceability_Report.xlsx")

        # Load and parse Jira issues
        print("\nLoading Jira data...")
        df = load_and_parse_jira_issues(jira_file)
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
        generate_excel_report(output_file, df, summary_df, fuzzy_matches)

        # Print summary
        print_summary(df, len(fuzzy_matches), str(output_file))

        return 0

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        return 1
    except ValueError as e:
        print(f"\nERROR: {e}")
        return 1
    except Exception as e:
        print(f"\nERROR: Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
