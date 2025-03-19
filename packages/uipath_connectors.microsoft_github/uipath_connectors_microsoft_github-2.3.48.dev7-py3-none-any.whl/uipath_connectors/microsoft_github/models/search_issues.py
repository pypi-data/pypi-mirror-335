from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_issues_author_association import SearchIssuesAuthorAssociation
import datetime
from ..models.search_issues_milestone import SearchIssuesMilestone
from ..models.search_issues_performed_via_github_app import (
    SearchIssuesPerformedViaGithubApp,
)
from ..models.search_issues_reactions import SearchIssuesReactions
from ..models.search_issues_pull_request import SearchIssuesPullRequest
from ..models.search_issues_assignees_array_item_ref import (
    SearchIssuesAssigneesArrayItemRef,
)
from ..models.search_issues_repository import SearchIssuesRepository
from ..models.search_issues_text_matches_array_item_ref import (
    SearchIssuesTextMatchesArrayItemRef,
)
from ..models.search_issues_labels_array_item_ref import SearchIssuesLabelsArrayItemRef
from ..models.search_issues_assignee import SearchIssuesAssignee
from ..models.search_issues_user import SearchIssuesUser


class SearchIssues(BaseModel):
    """
    Attributes:
        active_lock_reason (Optional[str]):
        assignee (Optional[SearchIssuesAssignee]):
        assignees (Optional[list['SearchIssuesAssigneesArrayItemRef']]):
        author_association (Optional[SearchIssuesAuthorAssociation]): How the author is associated with the repository.
                Example: OWNER.
        body (Optional[str]):
        body_html (Optional[str]):
        body_text (Optional[str]):
        closed_at (Optional[datetime.datetime]):
        comments (Optional[int]):
        comments_url (Optional[str]):
        created_at (Optional[datetime.datetime]):
        draft (Optional[bool]):
        events_url (Optional[str]):
        html_url (Optional[str]):
        id (Optional[int]):
        labels (Optional[list['SearchIssuesLabelsArrayItemRef']]):
        labels_url (Optional[str]):
        locked (Optional[bool]):
        milestone (Optional[SearchIssuesMilestone]):
        node_id (Optional[str]):
        number (Optional[int]):
        performed_via_github_app (Optional[SearchIssuesPerformedViaGithubApp]):
        pull_request (Optional[SearchIssuesPullRequest]):
        reactions (Optional[SearchIssuesReactions]):
        repository (Optional[SearchIssuesRepository]):
        repository_url (Optional[str]):
        score (Optional[float]):
        state (Optional[str]):
        state_reason (Optional[str]):
        text_matches (Optional[list['SearchIssuesTextMatchesArrayItemRef']]):
        timeline_url (Optional[str]):
        title (Optional[str]):
        updated_at (Optional[datetime.datetime]):
        url (Optional[str]):
        user (Optional[SearchIssuesUser]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    active_lock_reason: Optional[str] = Field(alias="active_lock_reason", default=None)
    assignee: Optional["SearchIssuesAssignee"] = Field(alias="assignee", default=None)
    assignees: Optional[list["SearchIssuesAssigneesArrayItemRef"]] = Field(
        alias="assignees", default=None
    )
    author_association: Optional[SearchIssuesAuthorAssociation] = Field(
        alias="author_association", default=None
    )
    body: Optional[str] = Field(alias="body", default=None)
    body_html: Optional[str] = Field(alias="body_html", default=None)
    body_text: Optional[str] = Field(alias="body_text", default=None)
    closed_at: Optional[datetime.datetime] = Field(alias="closed_at", default=None)
    comments: Optional[int] = Field(alias="comments", default=None)
    comments_url: Optional[str] = Field(alias="comments_url", default=None)
    created_at: Optional[datetime.datetime] = Field(alias="created_at", default=None)
    draft: Optional[bool] = Field(alias="draft", default=None)
    events_url: Optional[str] = Field(alias="events_url", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    labels: Optional[list["SearchIssuesLabelsArrayItemRef"]] = Field(
        alias="labels", default=None
    )
    labels_url: Optional[str] = Field(alias="labels_url", default=None)
    locked: Optional[bool] = Field(alias="locked", default=None)
    milestone: Optional["SearchIssuesMilestone"] = Field(
        alias="milestone", default=None
    )
    node_id: Optional[str] = Field(alias="node_id", default=None)
    number: Optional[int] = Field(alias="number", default=None)
    performed_via_github_app: Optional["SearchIssuesPerformedViaGithubApp"] = Field(
        alias="performed_via_github_app", default=None
    )
    pull_request: Optional["SearchIssuesPullRequest"] = Field(
        alias="pull_request", default=None
    )
    reactions: Optional["SearchIssuesReactions"] = Field(
        alias="reactions", default=None
    )
    repository: Optional["SearchIssuesRepository"] = Field(
        alias="repository", default=None
    )
    repository_url: Optional[str] = Field(alias="repository_url", default=None)
    score: Optional[float] = Field(alias="score", default=None)
    state: Optional[str] = Field(alias="state", default=None)
    state_reason: Optional[str] = Field(alias="state_reason", default=None)
    text_matches: Optional[list["SearchIssuesTextMatchesArrayItemRef"]] = Field(
        alias="text_matches", default=None
    )
    timeline_url: Optional[str] = Field(alias="timeline_url", default=None)
    title: Optional[str] = Field(alias="title", default=None)
    updated_at: Optional[datetime.datetime] = Field(alias="updated_at", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    user: Optional["SearchIssuesUser"] = Field(alias="user", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchIssues"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
