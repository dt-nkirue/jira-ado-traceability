"""Data models for Jira-ADO traceability."""

from dataclasses import dataclass
from datetime import datetime
from typing import TypedDict


class JiraIssue(TypedDict, total=False):
    """Jira issue data structure."""

    key: str
    summary: str
    status: str
    status_category: str
    priority: str
    severity: str
    assignee: str
    created: datetime | None
    resolved: datetime | None
    ado_id: str
    ado_state_jira: str


class AdoWorkItem(TypedDict):
    """ADO work item data structure.

    All fields are required to ensure type safety.
    """

    id: str
    title: str
    state: str
    assigned_to: str
    work_item_type: str
    priority: str
    severity: str
    created_date: str
    closed_date: str
    resolved_date: str
    area_path: str
    iteration_path: str


class FuzzyMatch(TypedDict):
    """Fuzzy match result structure."""

    jira_key: str
    jira_summary: str
    jira_status: str
    potential_ado_id: str
    ado_title: str
    ado_state: str
    ado_work_item_type: str
    match_score: int
    confidence: str


@dataclass
class Config:
    """Configuration for Jira-ADO traceability."""

    # ADO Configuration
    ado_server: str
    ado_collection: str
    ado_project: str
    ado_pat: str

    # Jira Configuration
    jira_url: str | None = None
    jira_username: str | None = None
    jira_api_token: str | None = None
    jira_project_key: str | None = None
    jira_jql: str | None = None

    # File Configuration
    jira_data_file: str | None = None
    output_file: str | None = None
    data_source: str = "FILE"  # "API" or "FILE"

    # Matching Configuration
    fuzzy_match_threshold: int = 70
    fuzzy_match_limit: int = 5
    ado_scan_days: int = 90

    @property
    def ado_api_base(self) -> str:
        """Get ADO API base URL."""
        return f"{self.ado_server}/{self.ado_collection}/{self.ado_project}/_apis"
