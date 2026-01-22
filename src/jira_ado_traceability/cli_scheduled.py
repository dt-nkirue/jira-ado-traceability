"""CLI entry point for scheduled mode (config file based)."""

import argparse
import sys
from pathlib import Path

import pandas as pd

from jira_ado_traceability.ado_client import AdoClient
from jira_ado_traceability.comparator import add_comparison_columns
from jira_ado_traceability.config import Config, load_config_from_file
from jira_ado_traceability.excel_generator import generate_excel_report
from jira_ado_traceability.fuzzy_matcher import find_fuzzy_matches
from jira_ado_traceability.jira_client import fetch_jira_issues_from_api
from jira_ado_traceability.jira_parser import load_and_parse_jira_issues, parse_jira_issues
from jira_ado_traceability.models import AdoWorkItem, FuzzyMatch
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


def _load_config_and_paths(args: argparse.Namespace) -> tuple[Config, Path | None, Path] | tuple[None, None, None]:
    """Load configuration and resolve file paths.

    Args:
        args: Parsed command-line arguments

    Returns:
        Tuple of (config, jira_file, output_file) or (None, None, None) on error
    """
    print(f"Loading configuration from {args.config}...")
    config = load_config_from_file(args.config)

    # For FILE mode, require jira_data_file
    if config.data_source == "FILE" and not config.jira_data_file:
        print("ERROR: jira_data_file not specified in config for FILE mode")
        return None, None, None

    jira_file = Path(config.jira_data_file) if config.jira_data_file else None
    output_file = Path(config.output_file) if config.output_file else Path("Jira_ADO_Traceability_Report.xlsx")

    return config, jira_file, output_file


def _fetch_ado_work_items(df: pd.DataFrame, ado_client: AdoClient) -> dict[str, AdoWorkItem]:
    """Fetch ADO work items for linked Jira issues.

    Args:
        df: DataFrame with Jira issues
        ado_client: ADO API client

    Returns:
        Dictionary of ADO work items by ID
    """
    print("\nFetching Azure DevOps work items...")
    ado_ids = df[df["ADO ID"] != "Not Linked"]["ADO ID"].unique().tolist()
    print(f"Found {len(ado_ids)} unique ADO work items to fetch")
    return ado_client.fetch_work_items(ado_ids)


def _perform_fuzzy_matching(df: pd.DataFrame, ado_client: AdoClient, config: Config) -> list[FuzzyMatch]:
    """Perform fuzzy matching for unlinked Jira items.

    Args:
        df: DataFrame with Jira issues
        ado_client: ADO API client
        config: Configuration object

    Returns:
        List of fuzzy matches
    """
    print("\nPerforming fuzzy matching for unlinked Jira items...")
    print("Fetching all ADO work items for fuzzy matching...")
    all_ado_work_items = ado_client.query_recent_work_items(days=config.ado_scan_days)

    unlinked_df = df[df["ADO ID"] == "Not Linked"]
    return find_fuzzy_matches(
        unlinked_df,
        all_ado_work_items,
        threshold=config.fuzzy_match_threshold,
        limit=config.fuzzy_match_limit,
    )


def main() -> int:
    """Run traceability report in scheduled mode.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        args = parse_args()
        config, jira_file, output_file = _load_config_and_paths(args)

        if config is None or output_file is None:
            return 1

        # Load Jira data based on data source
        print("\n" + "=" * 70)
        print("JIRA-ADO TRACEABILITY REPORT")
        print("=" * 70)

        if config.data_source == "API":
            print("\n[MODE] API - Fetching data in real-time from Jira Cloud")
            jira_data = fetch_jira_issues_from_api(config)
            df = parse_jira_issues(jira_data)
            print(f"[SUCCESS] Loaded {len(df)} Jira issues from API")
        else:
            print("\n[MODE] FILE - Loading from static JSON file")
            if jira_file is None:
                print("ERROR: jira_file is required for FILE mode")
                return 1
            df = load_and_parse_jira_issues(jira_file)
            print(f"[SUCCESS] Loaded {len(df)} Jira issues from file")

        ado_client = AdoClient(config)
        ado_work_items = _fetch_ado_work_items(df, ado_client)
        fuzzy_matches = _perform_fuzzy_matching(df, ado_client, config)

        print("\nMerging Jira and ADO data...")
        df = add_comparison_columns(df, ado_work_items)

        print("\nGenerating summary statistics...")
        summary_df = generate_summary_statistics(df)

        actual_output_file = generate_excel_report(output_file, df, summary_df, fuzzy_matches)
        print_summary(df, len(fuzzy_matches), str(actual_output_file))

    except FileNotFoundError as e:
        print(f"\nERROR: {e}")
        return 1
    except ValueError as e:
        print(f"\nERROR: {e}")
        return 1
    except (OSError, KeyError) as e:
        print(f"\nERROR: Unexpected error: {e}")
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
