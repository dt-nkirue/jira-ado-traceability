"""Unit tests for ado_client module."""

from unittest.mock import Mock, patch

import pytest
import requests

from jira_ado_traceability.ado_client import AdoClient
from jira_ado_traceability.models import Config


@pytest.fixture
def test_config() -> Config:
    """Create test configuration."""
    return Config(
        ado_server="https://dev.azure.com",
        ado_collection="TestCollection",
        ado_project="TestProject",
        ado_pat="test-pat-token",
        output_file="test.xlsx",
    )


@pytest.fixture
def ado_client(test_config: Config) -> AdoClient:
    """Create ADO client with test config."""
    return AdoClient(test_config)


class TestAdoClientInit:
    """Tests for AdoClient initialization."""

    def test_client_initialization(self, ado_client: AdoClient, test_config: Config) -> None:
        """Test client initializes with correct config."""
        assert ado_client.config == test_config
        assert ado_client.auth.username == ""
        assert ado_client.auth.password == "test-pat-token"  # S105: test fixture, not real credential
        assert "TestProject/_apis" in ado_client.api_base


class TestFetchWorkItem:
    """Tests for fetch_work_item method."""

    def test_fetch_successful(self, ado_client: AdoClient) -> None:
        """Test successfully fetching a work item."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12345,
            "fields": {
                "System.Title": "Test Work Item",
                "System.State": "Active",
                "System.AssignedTo": {"displayName": "Jane Doe"},
                "System.WorkItemType": "Bug",
                "Microsoft.VSTS.Common.Priority": 2,
                "Microsoft.VSTS.Common.Severity": "3",
                "System.CreatedDate": "2024-01-15T10:00:00Z",
                "Microsoft.VSTS.Common.ClosedDate": "",
                "Microsoft.VSTS.Common.ResolvedDate": "2024-01-20T14:00:00Z",
                "System.AreaPath": "Project\\Area",
                "System.IterationPath": "Project\\Iteration1",
            },
        }

        with patch("requests.get", return_value=mock_response):
            result = ado_client.fetch_work_item("12345")

        assert result is not None
        assert result["id"] == "12345"
        assert result["title"] == "Test Work Item"
        assert result["state"] == "Active"
        assert result["assigned_to"] == "Jane Doe"
        assert result["work_item_type"] == "Bug"

    def test_fetch_with_string_assigned_to(self, ado_client: AdoClient) -> None:
        """Test fetching work item with assigned_to as string."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 12345,
            "fields": {
                "System.Title": "Test",
                "System.State": "Active",
                "System.AssignedTo": "John Doe",  # String instead of dict
                "System.WorkItemType": "Task",
            },
        }

        with patch("requests.get", return_value=mock_response):
            result = ado_client.fetch_work_item("12345")

        assert result is not None
        assert result["assigned_to"] == "John Doe"

    def test_fetch_http_error(self, ado_client: AdoClient) -> None:
        """Test handling HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404

        with patch("requests.get", return_value=mock_response):
            result = ado_client.fetch_work_item("99999")

        assert result is not None
        assert result["state"] == "Error"
        assert "HTTP 404" in result["title"]

    def test_fetch_request_exception(self, ado_client: AdoClient) -> None:
        """Test handling request exception."""
        with patch("requests.get", side_effect=requests.RequestException("Connection error")):
            result = ado_client.fetch_work_item("12345")

        assert result is not None
        assert result["state"] == "Error"
        assert "ERROR" in result["title"]


class TestFetchWorkItems:
    """Tests for fetch_work_items method."""

    def test_fetch_multiple_items(self, ado_client: AdoClient) -> None:
        """Test fetching multiple work items."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "fields": {
                "System.Title": "Item",
                "System.State": "Active",
                "System.WorkItemType": "Task",
            },
        }

        with patch("requests.get", return_value=mock_response):
            result = ado_client.fetch_work_items(["123", "456"])

        assert len(result) == 2
        assert "123" in result
        assert "456" in result

    def test_fetch_skips_invalid_ids(self, ado_client: AdoClient) -> None:
        """Test that invalid IDs are skipped."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 123,
            "fields": {"System.Title": "Valid", "System.State": "Active"},
        }

        with patch("requests.get", return_value=mock_response):
            result = ado_client.fetch_work_items(["123", "", "Not Linked"])

        assert len(result) == 1
        assert "123" in result


class TestQueryRecentWorkItems:
    """Tests for query_recent_work_items method."""

    def test_query_successful(self, ado_client: AdoClient) -> None:
        """Test successful WIQL query."""
        # Mock WIQL query response
        mock_wiql_response = Mock()
        mock_wiql_response.status_code = 200
        mock_wiql_response.json.return_value = {"workItems": [{"id": 1}, {"id": 2}]}

        # Mock individual work item fetches
        mock_item_response = Mock()
        mock_item_response.status_code = 200
        mock_item_response.json.return_value = {
            "fields": {
                "System.Title": "Test Item",
                "System.State": "Active",
                "System.WorkItemType": "Bug",
            }
        }

        with (
            patch("requests.post", return_value=mock_wiql_response),
            patch("requests.get", return_value=mock_item_response),
        ):
            result = ado_client.query_recent_work_items(days=30)

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[0]["title"] == "Test Item"

    def test_query_with_invalid_days(self, ado_client: AdoClient) -> None:
        """Test query with negative days raises error."""
        with pytest.raises(ValueError, match="Invalid days parameter"):
            ado_client.query_recent_work_items(days=-10)

    def test_query_http_error(self, ado_client: AdoClient) -> None:
        """Test query with HTTP error returns empty list."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch("requests.post", return_value=mock_response):
            result = ado_client.query_recent_work_items(days=90)

        assert result == []

    def test_query_request_exception(self, ado_client: AdoClient) -> None:
        """Test query with request exception returns empty list."""
        with patch("requests.post", side_effect=requests.RequestException("Network error")):
            result = ado_client.query_recent_work_items(days=90)

        assert result == []

    def test_query_limits_to_200_items(self, ado_client: AdoClient) -> None:
        """Test that query result is limited to 200 items."""
        # Create 250 work items
        work_items = [{"id": i} for i in range(250)]
        mock_wiql_response = Mock()
        mock_wiql_response.status_code = 200
        mock_wiql_response.json.return_value = {"workItems": work_items}

        mock_item_response = Mock()
        mock_item_response.status_code = 200
        mock_item_response.json.return_value = {
            "fields": {
                "System.Title": "Item",
                "System.State": "Active",
                "System.WorkItemType": "Task",
            }
        }

        with (
            patch("requests.post", return_value=mock_wiql_response),
            patch("requests.get", return_value=mock_item_response),
        ):
            result = ado_client.query_recent_work_items(days=90)

        assert len(result) == 200  # Limited to 200
