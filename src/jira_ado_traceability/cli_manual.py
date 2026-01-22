"""CLI entry point for manual mode (environment variable based)."""

from jira_ado_traceability.ado_client import AdoClient
from jira_ado_traceability.comparator import add_comparison_columns
from jira_ado_traceability.config import create_manual_config
from jira_ado_traceability.excel_generator import generate_excel_report
from jira_ado_traceability.fuzzy_matcher import find_fuzzy_matches
from jira_ado_traceability.jira_client import fetch_jira_issues_from_api
from jira_ado_traceability.jira_parser import load_and_parse_jira_issues, parse_jira_issues
from jira_ado_traceability.reporter import generate_summary_statistics, print_summary


def main() -> None:
    """Run traceability report in manual mode."""
    # Configuration (loads from .env file or environment variables)
    config = create_manual_config()

    # Validate required configuration
    if not config.output_file:
        msg = "Output file path is required"
        raise ValueError(msg)

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
        if not config.jira_data_file:
            msg = "JIRA_INPUT_FILE is required when DATA_SOURCE=FILE"
            raise ValueError(msg)
        df = load_and_parse_jira_issues(config.jira_data_file)
        print(f"[SUCCESS] Loaded {len(df)} Jira issues from file")

    # Check if we have any issues
    if len(df) == 0:
        print("\n[WARN] No Jira issues found. Cannot generate report.")
        print("Please check your JQL query or Jira data file.")
        return

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
    actual_output_file = generate_excel_report(config.output_file, df, summary_df, fuzzy_matches)

    # Print summary
    print_summary(df, len(fuzzy_matches), str(actual_output_file))


if __name__ == "__main__":
    main()
