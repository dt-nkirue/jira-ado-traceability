"""Configuration management for Jira-ADO traceability."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from jira_ado_traceability.models import Config

# Load environment variables from .env file
load_dotenv()


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
    ado_server: str | None = None,
    ado_collection: str | None = None,
    ado_project: str | None = None,
    ado_pat: str | None = None,
    jira_data_file: str | None = None,
    output_file: str | None = None,
) -> Config:
    """Create configuration for manual mode.

    Loads from environment variables by default, with optional overrides.

    Args:
        ado_server: ADO server URL (defaults to ADO_SERVER env var)
        ado_collection: ADO collection name (defaults to ADO_COLLECTION env var)
        ado_project: ADO project name (defaults to ADO_PROJECT env var)
        ado_pat: ADO personal access token (defaults to ADO_PAT env var)
        jira_data_file: Path to Jira data JSON file (defaults to JIRA_INPUT_FILE env var)
        output_file: Output Excel file path (defaults to OUTPUT_FILE env var)

    Returns:
        Config object

    Raises:
        ValueError: If required environment variables are missing
    """
    # Load ADO config from environment variables with fallbacks
    ado_server = ado_server or os.getenv("ADO_SERVER")
    ado_collection = ado_collection or os.getenv("ADO_COLLECTION")
    ado_project = ado_project or os.getenv("ADO_PROJECT")
    ado_pat = ado_pat or os.getenv("ADO_PAT")

    # Load Jira config from environment variables
    jira_url = os.getenv("JIRA_URL")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    jira_project_key = os.getenv("JIRA_PROJECT_KEY")
    jira_jql = os.getenv("JIRA_JQL")

    # Load file paths and data source
    jira_data_file = jira_data_file or os.getenv("JIRA_INPUT_FILE")
    output_file = output_file or os.getenv("OUTPUT_FILE")
    data_source = os.getenv("DATA_SOURCE", "FILE")

    # Validate required ADO fields
    if not ado_server:
        msg = "ADO_SERVER not found in environment variables or parameters"
        raise ValueError(msg)
    if not ado_collection:
        msg = "ADO_COLLECTION not found in environment variables or parameters"
        raise ValueError(msg)
    if not ado_project:
        msg = "ADO_PROJECT not found in environment variables or parameters"
        raise ValueError(msg)
    if not ado_pat:
        msg = "ADO_PAT not found in environment variables or parameters"
        raise ValueError(msg)

    # Validate based on data source
    if data_source == "API":
        if not jira_url:
            msg = "JIRA_URL required when DATA_SOURCE=API"
            raise ValueError(msg)
        if not jira_username:
            msg = "JIRA_USERNAME required when DATA_SOURCE=API"
            raise ValueError(msg)
        if not jira_api_token:
            msg = "JIRA_API_TOKEN required when DATA_SOURCE=API"
            raise ValueError(msg)
    elif data_source == "FILE":
        if not jira_data_file:
            msg = "JIRA_INPUT_FILE required when DATA_SOURCE=FILE"
            raise ValueError(msg)

    if not output_file:
        msg = "OUTPUT_FILE not found in environment variables or parameters"
        raise ValueError(msg)

    return Config(
        ado_server=ado_server,
        ado_collection=ado_collection,
        ado_project=ado_project,
        ado_pat=ado_pat,
        jira_url=jira_url,
        jira_username=jira_username,
        jira_api_token=jira_api_token,
        jira_project_key=jira_project_key,
        jira_jql=jira_jql,
        jira_data_file=jira_data_file,
        output_file=output_file,
        data_source=data_source,
    )
