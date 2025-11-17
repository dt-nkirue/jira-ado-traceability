"""Unit tests for config module."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from jira_ado_traceability.config import (
    create_manual_config,
    load_config_from_file,
)


class TestLoadConfigFromFile:
    """Tests for load_config_from_file function."""

    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Test loading a valid configuration file."""
        config_file = tmp_path / "config.json"
        config_data = """{
            "ado_server": "https://dev.azure.com",
            "ado_collection": "MyCollection",
            "ado_project": "MyProject",
            "ado_pat": "test-pat-token",
            "jira_data_file": "jira_data.json",
            "output_file": "output.xlsx",
            "fuzzy_match_threshold": 80,
            "fuzzy_match_limit": 10,
            "ado_scan_days": 60
        }"""
        config_file.write_text(config_data)

        # Clear environment to test config file values
        with patch.dict(os.environ, {}, clear=True):
            config = load_config_from_file(config_file)

        assert config.ado_server == "https://dev.azure.com"
        assert config.ado_collection == "MyCollection"
        assert config.ado_project == "MyProject"
        assert config.ado_pat == "test-pat-token"
        assert config.jira_data_file == "jira_data.json"
        assert config.output_file == "output.xlsx"
        assert config.fuzzy_match_threshold == 80
        assert config.fuzzy_match_limit == 10
        assert config.ado_scan_days == 60

    def test_load_config_with_env_override(self, tmp_path: Path) -> None:
        """Test that environment variable overrides config file."""
        config_file = tmp_path / "config.json"
        config_data = """{
            "ado_server": "https://dev.azure.com",
            "ado_collection": "MyCollection",
            "ado_project": "MyProject",
            "ado_pat": "file-pat-token"
        }"""
        config_file.write_text(config_data)

        with patch.dict(os.environ, {"ADO_PAT": "env-pat-token"}):
            config = load_config_from_file(config_file)

        assert config.ado_pat == "env-pat-token"

    def test_load_config_missing_file(self) -> None:
        """Test loading non-existent config file raises error."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_config_from_file("nonexistent.json")

    def test_load_config_missing_ado_pat(self, tmp_path: Path) -> None:
        """Test loading config without ADO PAT raises error."""
        config_file = tmp_path / "config.json"
        config_data = """{
            "ado_server": "https://dev.azure.com",
            "ado_collection": "MyCollection",
            "ado_project": "MyProject"
        }"""
        config_file.write_text(config_data)

        with patch.dict(os.environ, {}, clear=True), pytest.raises(ValueError, match="ADO_PAT not found"):
            load_config_from_file(config_file)

    def test_load_config_with_defaults(self, tmp_path: Path) -> None:
        """Test that default values are applied."""
        config_file = tmp_path / "config.json"
        config_data = """{
            "ado_server": "https://dev.azure.com",
            "ado_collection": "MyCollection",
            "ado_project": "MyProject",
            "ado_pat": "test-pat"
        }"""
        config_file.write_text(config_data)

        config = load_config_from_file(config_file)

        assert config.fuzzy_match_threshold == 70  # Default
        assert config.fuzzy_match_limit == 5  # Default
        assert config.ado_scan_days == 90  # Default


class TestCreateManualConfig:
    """Tests for create_manual_config function."""

    @patch.dict(
        os.environ,
        {
            "ADO_SERVER": "https://dev.azure.com",
            "ADO_COLLECTION": "TestCollection",
            "ADO_PROJECT": "TestProject",
            "ADO_PAT": "test-pat-123",
            "JIRA_INPUT_FILE": "test_jira.json",
            "OUTPUT_FILE": "test_output.xlsx",
            "DATA_SOURCE": "FILE",
        },
    )
    def test_create_config_from_env(self) -> None:
        """Test creating config from environment variables."""
        config = create_manual_config()

        assert config.ado_server == "https://dev.azure.com"
        assert config.ado_collection == "TestCollection"
        assert config.ado_project == "TestProject"
        assert config.ado_pat == "test-pat-123"
        assert config.jira_data_file == "test_jira.json"
        assert config.output_file == "test_output.xlsx"
        assert config.data_source == "FILE"

    @patch.dict(
        os.environ,
        {
            "ADO_SERVER": "https://dev.azure.com",
            "ADO_COLLECTION": "TestCollection",
            "ADO_PROJECT": "TestProject",
            "ADO_PAT": "env-pat",
            "OUTPUT_FILE": "env_output.xlsx",
            "DATA_SOURCE": "FILE",
            "JIRA_INPUT_FILE": "env_jira.json",
        },
    )
    def test_create_config_with_overrides(self) -> None:
        """Test that function parameters override environment variables."""
        config = create_manual_config(
            ado_pat="override-pat",
            jira_data_file="override_jira.json",
            output_file="override_output.xlsx",
        )

        assert config.ado_pat == "override-pat"
        assert config.jira_data_file == "override_jira.json"
        assert config.output_file == "override_output.xlsx"

    @patch.dict(os.environ, {}, clear=True)
    def test_create_config_missing_ado_server(self) -> None:
        """Test missing ADO_SERVER raises error."""
        with pytest.raises(ValueError, match="ADO_SERVER not found"):
            create_manual_config()

    def test_create_config_missing_ado_pat(self) -> None:
        """Test missing ADO_PAT raises error."""
        with (
            patch.dict(
                os.environ,
                {
                    "ADO_SERVER": "https://dev.azure.com",
                    "ADO_COLLECTION": "TestCollection",
                    "ADO_PROJECT": "TestProject",
                },
                clear=True,
            ),
            pytest.raises(ValueError, match="ADO_PAT not found"),
        ):
            create_manual_config()

    def test_create_config_missing_output_file(self) -> None:
        """Test missing OUTPUT_FILE raises error."""
        with (
            patch.dict(
                os.environ,
                {
                    "ADO_SERVER": "https://dev.azure.com",
                    "ADO_COLLECTION": "TestCollection",
                    "ADO_PROJECT": "TestProject",
                    "ADO_PAT": "test-pat",
                    "DATA_SOURCE": "FILE",
                    "JIRA_INPUT_FILE": "test.json",
                },
                clear=True,
            ),
            pytest.raises(ValueError, match="OUTPUT_FILE not found"),
        ):
            create_manual_config()

    def test_create_config_api_mode_missing_jira_url(self) -> None:
        """Test API mode without JIRA_URL raises error."""
        with (
            patch.dict(
                os.environ,
                {
                    "ADO_SERVER": "https://dev.azure.com",
                    "ADO_COLLECTION": "TestCollection",
                    "ADO_PROJECT": "TestProject",
                    "ADO_PAT": "test-pat",
                    "OUTPUT_FILE": "output.xlsx",
                    "DATA_SOURCE": "API",
                },
                clear=True,
            ),
            pytest.raises(ValueError, match="JIRA_URL required when DATA_SOURCE=API"),
        ):
            create_manual_config()

    def test_create_config_file_mode_missing_jira_file(self) -> None:
        """Test FILE mode without JIRA_INPUT_FILE raises error."""
        with (
            patch.dict(
                os.environ,
                {
                    "ADO_SERVER": "https://dev.azure.com",
                    "ADO_COLLECTION": "TestCollection",
                    "ADO_PROJECT": "TestProject",
                    "ADO_PAT": "test-pat",
                    "OUTPUT_FILE": "output.xlsx",
                    "DATA_SOURCE": "FILE",
                },
                clear=True,
            ),
            pytest.raises(ValueError, match="JIRA_INPUT_FILE required when DATA_SOURCE=FILE"),
        ):
            create_manual_config()
