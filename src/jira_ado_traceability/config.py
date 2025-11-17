"""Configuration management for Jira-ADO traceability."""

import json
import os
from pathlib import Path

from jira_ado_traceability.models import Config


def load_config_from_file(config_path: str | Path) -> Config:
    """Load configuration from JSON file.

    Args:
        config_path: Path to configuration JSON file

    Returns:
        Config object with loaded settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file is invalid
    """
    config_file = Path(config_path)

    if not config_file.exists():
        msg = f"Configuration file not found: {config_path}"
        raise FileNotFoundError(msg)

    with config_file.open(encoding="utf-8") as f:
        config_data = json.load(f)

    # Get ADO PAT from environment variable or config
    ado_pat = os.environ.get("ADO_PAT", config_data.get("ado_pat", ""))

    if not ado_pat:
        msg = "ADO_PAT not found in environment or config file"
        raise ValueError(msg)

    return Config(
        ado_server=config_data.get("ado_server", ""),
        ado_collection=config_data.get("ado_collection", ""),
        ado_project=config_data.get("ado_project", ""),
        ado_pat=ado_pat,
        jira_data_file=config_data.get("jira_data_file"),
        output_file=config_data.get("output_file"),
        fuzzy_match_threshold=config_data.get("fuzzy_match_threshold", 70),
        fuzzy_match_limit=config_data.get("fuzzy_match_limit", 5),
        ado_scan_days=config_data.get("ado_scan_days", 90),
    )


def create_manual_config(
    ado_server: str,
    ado_collection: str,
    ado_project: str,
    ado_pat: str,
    jira_data_file: str,
    output_file: str,
) -> Config:
    """Create configuration for manual mode.

    Args:
        ado_server: ADO server URL
        ado_collection: ADO collection name
        ado_project: ADO project name
        ado_pat: ADO personal access token
        jira_data_file: Path to Jira data JSON file
        output_file: Output Excel file path

    Returns:
        Config object
    """
    return Config(
        ado_server=ado_server,
        ado_collection=ado_collection,
        ado_project=ado_project,
        ado_pat=ado_pat,
        jira_data_file=jira_data_file,
        output_file=output_file,
    )
