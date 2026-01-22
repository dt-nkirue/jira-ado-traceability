"""Azure DevOps API client for fetching work items."""

from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from jira_ado_traceability.models import AdoWorkItem, Config


class AdoClient:
    """Client for interacting with Azure DevOps REST API."""

    def __init__(self, config: Config) -> None:
        """Initialize ADO client.

        Args:
            config: Configuration object with ADO settings
        """
        self.config = config
        self.auth = HTTPBasicAuth("", config.ado_pat)
        self.api_base = config.ado_api_base

    def fetch_work_item(self, work_item_id: str) -> AdoWorkItem | None:
        """Fetch a single work item from ADO.

        Args:
            work_item_id: ADO work item ID

        Returns:
            AdoWorkItem dictionary or None if fetch fails
        """
        try:
            url = f"{self.api_base}/wit/workitems/{work_item_id}?api-version=5.0"
            response = requests.get(url, auth=self.auth, timeout=10)

            if response.status_code == 200:
                work_item = response.json()
                return self._parse_work_item(work_item)
            else:
                # Non-200 status code
                print(f"  [FAIL] Failed to fetch ADO-{work_item_id}: HTTP {response.status_code}")
                return None
        except requests.RequestException as e:
            print(f"  [ERROR] Error fetching ADO-{work_item_id}: {e!s}")
            return None

    def _parse_work_item(self, work_item: dict[str, Any]) -> AdoWorkItem:
        """Parse work item response into structured format.

        Args:
            work_item: Raw work item JSON from ADO API

        Returns:
            Parsed AdoWorkItem
        """
        fields: dict[str, Any] = work_item.get("fields", {})

        # Handle assigned to field (can be dict or string)
        assigned_to_raw = fields.get("System.AssignedTo", "Unassigned")
        assigned_to: str
        if isinstance(assigned_to_raw, dict):
            assigned_to = str(assigned_to_raw.get("displayName", "Unassigned"))
        else:
            assigned_to = str(assigned_to_raw)

        return AdoWorkItem(
            id=str(work_item.get("id", "")),
            title=str(fields.get("System.Title", "")),
            state=str(fields.get("System.State", "")),
            assigned_to=assigned_to,
            work_item_type=str(fields.get("System.WorkItemType", "")),
            priority=str(fields.get("Microsoft.VSTS.Common.Priority", "")),
            severity=str(fields.get("Microsoft.VSTS.Common.Severity", "")),
            created_date=str(fields.get("System.CreatedDate", "")),
            closed_date=str(fields.get("Microsoft.VSTS.Common.ClosedDate", "")),
            resolved_date=str(fields.get("Microsoft.VSTS.Common.ResolvedDate", "")),
            area_path=str(fields.get("System.AreaPath", "")),
            iteration_path=str(fields.get("System.IterationPath", "")),
        )

    def fetch_work_items(self, work_item_ids: list[str]) -> dict[str, AdoWorkItem]:
        """Fetch multiple work items from ADO.

        Args:
            work_item_ids: List of work item IDs to fetch

        Returns:
            Dictionary mapping work item IDs to AdoWorkItem objects
        """
        work_items = {}

        for work_item_id in work_item_ids:
            if not work_item_id or work_item_id == "Not Linked":
                continue

            print(f"Fetching ADO work item {work_item_id}...")
            item = self.fetch_work_item(work_item_id)

            if item:
                work_items[work_item_id] = item
                print(f"  [OK] Successfully fetched ADO-{work_item_id}: {item['state']}")

        return work_items

    def query_recent_work_items(self, days: int = 90) -> list[dict[str, Any]]:
        """Query recent work items using WIQL.

        Args:
            days: Number of days to look back

        Returns:
            List of work items with basic info
        """
        # Validate inputs to prevent injection (WIQL syntax, not SQL)
        if days < 0:
            msg = f"Invalid days parameter: {days}"
            raise ValueError(msg)

        # Project name comes from validated config, escape single quotes for WIQL safety
        project = self.config.ado_project.replace("'", "''")

        # Build WIQL query using validated parameters
        query_text = (
            f"SELECT [System.Id], [System.Title] "
            f"FROM WorkItems "
            f"WHERE [System.TeamProject] = '{project}' "
            f"AND [System.CreatedDate] >= @Today - {days} "
            f"ORDER BY [System.CreatedDate] DESC"
        )
        wiql_query = {"query": query_text}

        try:
            url = f"{self.api_base}/wit/wiql?api-version=5.0"
            response = requests.post(url, auth=self.auth, json=wiql_query, timeout=30)

            if response.status_code != 200:
                print(f"Could not fetch ADO work items for fuzzy matching: HTTP {response.status_code}")
                return []

            results = response.json()
            work_item_ids = [str(item["id"]) for item in results.get("workItems", [])]
            print(f"Found {len(work_item_ids)} ADO work items for potential matching")
            return self._fetch_work_items_for_fuzzy(work_item_ids[:200])

        except requests.RequestException as e:
            print(f"Error during fuzzy matching setup: {e!s}")
            return []

    def _fetch_work_items_for_fuzzy(self, work_item_ids: list[str]) -> list[dict[str, Any]]:
        """Fetch work items for fuzzy matching (limited fields).

        Args:
            work_item_ids: List of work item IDs

        Returns:
            List of work items with id, title, state, type
        """
        work_items: list[dict[str, Any]] = []

        for work_item_id in work_item_ids:
            try:
                url = f"{self.api_base}/wit/workitems/{work_item_id}?api-version=5.0"
                response = requests.get(url, auth=self.auth, timeout=10)

                if response.status_code == 200:
                    work_item = response.json()
                    fields: dict[str, Any] = work_item.get("fields", {})
                    work_item_dict: dict[str, Any] = {
                        "id": work_item_id,
                        "title": str(fields.get("System.Title", "")),
                        "state": str(fields.get("System.State", "")),
                        "work_item_type": str(fields.get("System.WorkItemType", "")),
                    }
                    work_items.append(work_item_dict)
            except requests.RequestException as e:
                print(f"  [WARN] Skipping work item {work_item_id}: {e!s}")
                continue

        return work_items
