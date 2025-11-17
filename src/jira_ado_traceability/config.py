"""Configuration management for Jira-ADO traceability."""

import json
import os
from pathlib import Path
from typing import Any

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
        config_data: dict[str, Any] = json.load(f)

    # Get ADO PAT from environment variable or config
    ado_pat = os.environ.get("ADO_PAT") or config_data.get("ado_pat", "")

    if not ado_pat:
        msg = "ADO_PAT not found in environment or config file"
        raise ValueError(msg)

    # Extract string values with defaults
    ado_server = str(config_data.get("ado_server", ""))
    ado_collection = str(config_data.get("ado_collection", ""))
    ado_project = str(config_data.get("ado_project", ""))
    jira_data_file = config_data.get("jira_data_file")
    output_file = config_data.get("output_file")
    fuzzy_match_threshold = int(config_data.get("fuzzy_match_threshold", 70))
    fuzzy_match_limit = int(config_data.get("fuzzy_match_limit", 5))
    ado_scan_days = int(config_data.get("ado_scan_days", 90))

    # Jira API fields (for API mode) - can be overridden by environment variables
    jira_url = os.environ.get("JIRA_URL") or config_data.get("jira_url")
    jira_username = os.environ.get("JIRA_USERNAME") or config_data.get("jira_username")
    jira_api_token = os.environ.get("JIRA_API_TOKEN") or config_data.get("jira_api_token")
    jira_project_key = os.environ.get("JIRA_PROJECT_KEY") or config_data.get("jira_project_key")
    jira_jql = os.environ.get("JIRA_JQL") or config_data.get("jira_jql")
    data_source = os.environ.get("DATA_SOURCE") or config_data.get("data_source", "FILE")

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
        jira_data_file=str(jira_data_file) if jira_data_file else None,
        output_file=str(output_file) if output_file else None,
        data_source=data_source,
        fuzzy_match_threshold=fuzzy_match_threshold,
        fuzzy_match_limit=fuzzy_match_limit,
        ado_scan_days=ado_scan_days,
    )


def _validate_ado_config(
    ado_server: str | None,
    ado_collection: str | None,
    ado_project: str | None,
    ado_pat: str | None,
) -> None:
    """Validate required ADO configuration fields.

    Args:
        ado_server: ADO server URL
        ado_collection: ADO collection name
        ado_project: ADO project name
        ado_pat: ADO personal access token

    Raises:
        ValueError: If any required field is missing
    """
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


def _validate_jira_config(
    data_source: str,
    jira_url: str | None,
    jira_username: str | None,
    jira_api_token: str | None,
    jira_data_file: str | None,
) -> None:
    """Validate Jira configuration based on data source.

    Args:
        data_source: Data source mode (API or FILE)
        jira_url: Jira URL (for API mode)
        jira_username: Jira username (for API mode)
        jira_api_token: Jira API token (for API mode)
        jira_data_file: Path to Jira data file (for FILE mode)

    Raises:
        ValueError: If required fields are missing for the data source
    """
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


def _load_env_vars(ado_pat: str | None, jira_data_file: str | None, output_file: str | None) -> dict[str, str | None]:
    """Load environment variables with optional overrides.

    Args:
        ado_pat: Optional ADO PAT override
        jira_data_file: Optional Jira data file override
        output_file: Optional output file override

    Returns:
        Dictionary of environment variables
    """
    return {
        "ado_server": os.getenv("ADO_SERVER"),
        "ado_collection": os.getenv("ADO_COLLECTION"),
        "ado_project": os.getenv("ADO_PROJECT"),
        "ado_pat": ado_pat or os.getenv("ADO_PAT"),
        "jira_url": os.getenv("JIRA_URL"),
        "jira_username": os.getenv("JIRA_USERNAME"),
        "jira_api_token": os.getenv("JIRA_API_TOKEN"),
        "jira_project_key": os.getenv("JIRA_PROJECT_KEY"),
        "jira_jql": os.getenv("JIRA_JQL"),
        "jira_data_file": jira_data_file or os.getenv("JIRA_INPUT_FILE"),
        "output_file": output_file or os.getenv("OUTPUT_FILE"),
        "data_source": os.getenv("DATA_SOURCE", "FILE"),
    }


def create_manual_config(
    ado_pat: str | None = None,
    jira_data_file: str | None = None,
    output_file: str | None = None,
) -> Config:
    """Create configuration for manual mode.

    Loads from environment variables by default, with optional overrides.

    Args:
        ado_pat: ADO personal access token (defaults to ADO_PAT env var)
        jira_data_file: Path to Jira data JSON file (defaults to JIRA_INPUT_FILE env var)
        output_file: Output Excel file path (defaults to OUTPUT_FILE env var)

    Returns:
        Config object

    Raises:
        ValueError: If required environment variables are missing
    """
    env = _load_env_vars(ado_pat, jira_data_file, output_file)

    _validate_ado_config(env["ado_server"], env["ado_collection"], env["ado_project"], env["ado_pat"])
    _validate_jira_config(
        str(env["data_source"]), env["jira_url"], env["jira_username"], env["jira_api_token"], env["jira_data_file"]
    )

    if not env["output_file"]:
        msg = "OUTPUT_FILE not found in environment variables or parameters"
        raise ValueError(msg)

    # Type assertions after validation
    ado_server_val = str(env["ado_server"])
    ado_collection_val = str(env["ado_collection"])
    ado_project_val = str(env["ado_project"])
    ado_pat_val = str(env["ado_pat"])
    output_file_val = str(env["output_file"])
    data_source_val = str(env["data_source"])

    return Config(
        ado_server=ado_server_val,
        ado_collection=ado_collection_val,
        ado_project=ado_project_val,
        ado_pat=ado_pat_val,
        jira_url=env["jira_url"],
        jira_username=env["jira_username"],
        jira_api_token=env["jira_api_token"],
        jira_project_key=env["jira_project_key"],
        jira_jql=env["jira_jql"],
        jira_data_file=env["jira_data_file"],
        output_file=output_file_val,
        data_source=data_source_val,
    )
