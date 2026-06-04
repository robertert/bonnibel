from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class IntegrationProvider(Enum):
    GITHUB = "GITHUB"
    JIRA = "JIRA"
    CONFLUENCE = "CONFLUENCE"


class PullRequestStatus(Enum):
    OPEN = "OPEN"
    APPROVED = "APPROVED"
    DECLINED = "DECLINED"
    MERGED = "MERGED"
    CLOSED = "CLOSED"


class JiraTicketStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@dataclass
class ProjectIntegration:
    integration_id: Optional[int] = None
    project_id: int = 0
    external_id: str = ""
    provider: IntegrationProvider = IntegrationProvider.GITHUB
    access_token: str = ""
    is_active: bool = True


@dataclass
class GitBranchRef:
    task_id: int
    branch_name: str
    external_id: str
    url: str


@dataclass
class GitPullRequestRef:
    pull_request_external_id: str
    task_id: int
    reviewer_id: Optional[str]
    status: PullRequestStatus
    title: str
    url: str
    created_at: datetime
    updated_at: datetime


@dataclass
class JiraTicketRef:
    task_id: int
    ticket_external_id: str
    ticket_key: str
    url: str
    status: JiraTicketStatus


@dataclass
class DocsPageRef:
    task_id: int
    page_external_id: str
    title: str
    url: str