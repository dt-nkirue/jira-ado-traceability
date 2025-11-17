"""Jira Cloud API client for fetching issue data."""

from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from jira_ado_traceability.models import Config


class JiraClient:
    """Client for interacting with Jira Cloud REST API v3."""

    def __init__(self, config: Config) -> None:
        """Initialize Jira API client.

        Args:
            config: Configuration object with Jira credentials
        """
        self.config = config
        self.base_url = config.jira_url
        self.auth = HTTPBasicAuth(config.jira_username or "", config.jira_api_token or "")
        self.api_url = f"{self.base_url}/rest/api/3"

    def search_issues(self, jql: str | None = None, max_results: int = 1000) -> dict[str, Any]:
        """Search for issues using JQL.

        Args:
            jql: JQL query string (uses config default if not provided)
            max_results: Maximum number of results to return

        Returns:
            Dictionary containing search results with issues list

        Raises:
            requests.RequestException: If API request fails
        """
        query = jql or self.config.jira_jql or ""

        if not query:
            msg = "No JQL query provided"
            raise ValueError(msg)

        print(f"Fetching Jira issues with JQL: {query}")

        all_issues: list[dict[str, Any]] = []
        start_at = 0
        batch_size = min(max_results, 100)  # Jira API limit is 100 per request

        while len(all_issues) < max_results:
            try:
                response = self._fetch_issues_batch(query, start_at, batch_size)

                if response.status_code != 200:
                    print(f"  [ERROR] HTTP {response.status_code}: {response.text}")
                    break

                data = response.json()
                issues = data.get("issues", [])

                if not issues:
                    break

                all_issues.extend(issues)
                print(f"  Fetched {len(all_issues)} issues...")

                # Check if there are more results
                total = data.get("total", 0)
                if len(all_issues) >= total:
                    break

                start_at += batch_size

            except requests.RequestException as e:
                print(f"  [ERROR] Failed to fetch issues: {e}")
                break

        print(f"[SUCCESS] Retrieved {len(all_issues)} Jira issues")

        return {
            "issues": all_issues,
            "total": len(all_issues),
            "jql": query,
        }

    def _fetch_issues_batch(self, jql: str, start_at: int, max_results: int) -> requests.Response:
        """Fetch a batch of issues from Jira API.

        Args:
            jql: JQL query string
            start_at: Starting index for pagination
            max_results: Number of results to fetch

        Returns:
            Response object from API request
        """
        url = f"{self.api_url}/search/jql"

        fields = ",".join(
            [
                "summary",
                "status",
                "priority",
                "assignee",
                "created",
                "resolutiondate",
                "customfield_10042",  # Severity
                "customfield_10109",  # ADO ID
                "customfield_10110",  # ADO State
            ]
        )

        params = {
            "jql": jql,
            "startAt": start_at,
            "maxResults": max_results,
            "fields": fields,
        }

        return requests.get(
            url,
            params=params,
            auth=self.auth,
            headers={"Accept": "application/json"},
            timeout=30,
        )

    def get_issue(self, issue_key: str) -> dict[str, Any] | None:
        """Get a single issue by key.

        Args:
            issue_key: Jira issue key (e.g., "PROJ-123")

        Returns:
            Issue data dictionary or None if not found
        """
        url = f"{self.api_url}/issue/{issue_key}"

        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers={"Accept": "application/json"},
                timeout=10,
            )
        except requests.RequestException as e:
            print(f"  [ERROR] Failed to fetch issue {issue_key}: {e}")
            return None
        else:
            if response.status_code == 200:
                return response.json()

            # Non-200 status code
            print(f"  [WARN] Could not fetch issue {issue_key}: HTTP {response.status_code}")
            return None

    def test_connection(self) -> bool:
        """Test connection to Jira API.

        Returns:
            True if connection successful, False otherwise
        """
        url = f"{self.api_url}/myself"

        try:
            response = requests.get(
                url,
                auth=self.auth,
                headers={"Accept": "application/json"},
                timeout=10,
            )
        except requests.RequestException as e:
            print(f"[ERROR] Could not connect to Jira: {e}")
            return False
        else:
            if response.status_code == 200:
                user_data = response.json()
                print(f"[SUCCESS] Connected to Jira as: {user_data.get('displayName', 'Unknown')}")
                return True

            # Authentication failed
            print(f"[ERROR] Jira authentication failed: HTTP {response.status_code}")
            return False


def fetch_jira_issues_from_api(config: Config) -> dict[str, Any]:
    """Fetch Jira issues from API using configuration.

    Args:
        config: Configuration object with Jira credentials

    Returns:
        Dictionary with issues data in same format as JSON file

    Raises:
        ValueError: If configuration is invalid
    """
    # Validate required fields
    if not config.jira_url:
        msg = "JIRA_URL is required for API mode"
        raise ValueError(msg)

    if not config.jira_username:
        msg = "JIRA_USERNAME is required for API mode"
        raise ValueError(msg)

    if not config.jira_api_token:
        msg = "JIRA_API_TOKEN is required for API mode"
        raise ValueError(msg)

    print("\n[JIRA API] Connecting to Jira Cloud...")
    print(f"  URL: {config.jira_url}")
    print(f"  User: {config.jira_username}")

    client = JiraClient(config)

    # Test connection first
    if not client.test_connection():
        msg = "Failed to connect to Jira API. Check credentials and URL."
        raise ConnectionError(msg)

    # Fetch issues
    print("\n[JIRA API] Fetching issues...")
    return client.search_issues()
