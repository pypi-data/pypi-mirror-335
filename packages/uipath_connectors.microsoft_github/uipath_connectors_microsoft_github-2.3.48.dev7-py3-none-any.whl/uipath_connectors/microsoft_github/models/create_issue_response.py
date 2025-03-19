from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_issue_response_author_association import (
    CreateIssueResponseAuthorAssociation,
)
from ..models.create_issue_response_state import CreateIssueResponseState
import datetime
from ..models.create_issue_response_labels_array_item_ref import (
    CreateIssueResponseLabelsArrayItemRef,
)
from ..models.create_issue_response_repository import CreateIssueResponseRepository
from ..models.create_issue_response_assignees_array_item_ref import (
    CreateIssueResponseAssigneesArrayItemRef,
)
from ..models.create_issue_response_closed_by import CreateIssueResponseClosedBy
from ..models.create_issue_response_assignee import CreateIssueResponseAssignee
from ..models.create_issue_response_performed_via_github_app import (
    CreateIssueResponsePerformedViaGithubApp,
)
from ..models.create_issue_response_reactions import CreateIssueResponseReactions
from ..models.create_issue_response_user import CreateIssueResponseUser
from ..models.create_issue_response_pull_request import CreateIssueResponsePullRequest
from ..models.create_issue_response_milestone import CreateIssueResponseMilestone


class CreateIssueResponse(BaseModel):
    """
    Attributes:
        active_lock_reason (Optional[str]):
        assignee (Optional[CreateIssueResponseAssignee]):
        assignees (Optional[list['CreateIssueResponseAssigneesArrayItemRef']]):
        author_association (Optional[CreateIssueResponseAuthorAssociation]): How the author is associated with the
                repository. Example: OWNER.
        body (Optional[str]): The contents of the issue Example: It looks like the new widget form is broken on Safari.
                When I try and create the widget, Safari crashes. This is reproducible on 10.8, but not 10.9. Maybe a browser
                bug?.
        body_html (Optional[str]):
        body_text (Optional[str]):
        closed_at (Optional[datetime.datetime]):
        closed_by (Optional[CreateIssueResponseClosedBy]):
        comments (Optional[int]):
        comments_url (Optional[str]):
        created_at (Optional[datetime.datetime]):
        draft (Optional[bool]):
        events_url (Optional[str]):
        html_url (Optional[str]):
        id (Optional[int]): Issue ID
        labels (Optional[list['CreateIssueResponseLabelsArrayItemRef']]):
        labels_url (Optional[str]):
        locked (Optional[bool]):
        milestone (Optional[CreateIssueResponseMilestone]):
        node_id (Optional[str]):
        number (Optional[int]): Number uniquely identifying the issue within its repository Example: 42.0.
        performed_via_github_app (Optional[CreateIssueResponsePerformedViaGithubApp]):
        pull_request (Optional[CreateIssueResponsePullRequest]):
        reactions (Optional[CreateIssueResponseReactions]):
        repository (Optional[CreateIssueResponseRepository]):
        repository_url (Optional[str]):
        state (Optional[CreateIssueResponseState]): The open or closed state of the issue. Can be one of: open, closed
                Example: open.
        state_reason (Optional[str]): The reason for the current state Example: not_planned.
        timeline_url (Optional[str]):
        title (Optional[str]): The title of the issue Example: Widget creation fails in Safari on OS X 10.8.
        updated_at (Optional[datetime.datetime]):
        url (Optional[str]): URL for the issue Example: https://api.github.com/repositories/42/issues/1.
        user (Optional[CreateIssueResponseUser]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    active_lock_reason: Optional[str] = Field(alias="active_lock_reason", default=None)
    assignee: Optional["CreateIssueResponseAssignee"] = Field(
        alias="assignee", default=None
    )
    assignees: Optional[list["CreateIssueResponseAssigneesArrayItemRef"]] = Field(
        alias="assignees", default=None
    )
    author_association: Optional[CreateIssueResponseAuthorAssociation] = Field(
        alias="author_association", default=None
    )
    body: Optional[str] = Field(alias="body", default=None)
    body_html: Optional[str] = Field(alias="body_html", default=None)
    body_text: Optional[str] = Field(alias="body_text", default=None)
    closed_at: Optional[datetime.datetime] = Field(alias="closed_at", default=None)
    closed_by: Optional["CreateIssueResponseClosedBy"] = Field(
        alias="closed_by", default=None
    )
    comments: Optional[int] = Field(alias="comments", default=None)
    comments_url: Optional[str] = Field(alias="comments_url", default=None)
    created_at: Optional[datetime.datetime] = Field(alias="created_at", default=None)
    draft: Optional[bool] = Field(alias="draft", default=None)
    events_url: Optional[str] = Field(alias="events_url", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    labels: Optional[list["CreateIssueResponseLabelsArrayItemRef"]] = Field(
        alias="labels", default=None
    )
    labels_url: Optional[str] = Field(alias="labels_url", default=None)
    locked: Optional[bool] = Field(alias="locked", default=None)
    milestone: Optional["CreateIssueResponseMilestone"] = Field(
        alias="milestone", default=None
    )
    node_id: Optional[str] = Field(alias="node_id", default=None)
    number: Optional[int] = Field(alias="number", default=None)
    performed_via_github_app: Optional["CreateIssueResponsePerformedViaGithubApp"] = (
        Field(alias="performed_via_github_app", default=None)
    )
    pull_request: Optional["CreateIssueResponsePullRequest"] = Field(
        alias="pull_request", default=None
    )
    reactions: Optional["CreateIssueResponseReactions"] = Field(
        alias="reactions", default=None
    )
    repository: Optional["CreateIssueResponseRepository"] = Field(
        alias="repository", default=None
    )
    repository_url: Optional[str] = Field(alias="repository_url", default=None)
    state: Optional[CreateIssueResponseState] = Field(alias="state", default=None)
    state_reason: Optional[str] = Field(alias="state_reason", default=None)
    timeline_url: Optional[str] = Field(alias="timeline_url", default=None)
    title: Optional[str] = Field(alias="title", default=None)
    updated_at: Optional[datetime.datetime] = Field(alias="updated_at", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    user: Optional["CreateIssueResponseUser"] = Field(alias="user", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateIssueResponse"], src_dict: Dict[str, Any]):
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
