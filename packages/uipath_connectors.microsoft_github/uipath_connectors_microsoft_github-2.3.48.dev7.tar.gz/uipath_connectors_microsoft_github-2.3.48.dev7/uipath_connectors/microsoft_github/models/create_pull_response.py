from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_pull_response_author_association import (
    CreatePullResponseAuthorAssociation,
)
from ..models.create_pull_response_state import CreatePullResponseState
import datetime
from ..models.create_pull_response_links import CreatePullResponseLinks
from ..models.create_pull_response_head import CreatePullResponseHead
from ..models.create_pull_response_milestone import CreatePullResponseMilestone
from ..models.create_pull_response_labels_array_item_ref import (
    CreatePullResponseLabelsArrayItemRef,
)
from ..models.create_pull_response_user import CreatePullResponseUser
from ..models.create_pull_response_merged_by import CreatePullResponseMergedBy
from ..models.create_pull_response_base import CreatePullResponseBase
from ..models.create_pull_response_auto_merge import CreatePullResponseAutoMerge
from ..models.create_pull_response_requested_reviewers_array_item_ref import (
    CreatePullResponseRequestedReviewersArrayItemRef,
)
from ..models.create_pull_response_assignee import CreatePullResponseAssignee
from ..models.create_pull_response_requested_teams_array_item_ref import (
    CreatePullResponseRequestedTeamsArrayItemRef,
)
from ..models.create_pull_response_assignees_array_item_ref import (
    CreatePullResponseAssigneesArrayItemRef,
)


class CreatePullResponse(BaseModel):
    """
    Attributes:
        field_links (Optional[CreatePullResponseLinks]):
        active_lock_reason (Optional[str]):  Example: too heated.
        additions (Optional[int]):  Example: 100.0.
        assignee (Optional[CreatePullResponseAssignee]):
        assignees (Optional[list['CreatePullResponseAssigneesArrayItemRef']]):
        author_association (Optional[CreatePullResponseAuthorAssociation]): How the author is associated with the
                repository. Example: OWNER.
        auto_merge (Optional[CreatePullResponseAutoMerge]):
        base (Optional[CreatePullResponseBase]):
        body (Optional[str]): The contents of the pull request Example: Please pull these awesome changes.
        changed_files (Optional[int]):  Example: 5.0.
        closed_at (Optional[datetime.datetime]):  Example: 2011-01-26T19:01:12.0000000+00:00.
        comments (Optional[int]):  Example: 10.0.
        comments_url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-World/issues/1347/comments.
        commits (Optional[int]):  Example: 3.0.
        commits_url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-World/pulls/1347/commits.
        created_at (Optional[datetime.datetime]):  Example: 2011-01-26T19:01:12.0000000+00:00.
        deletions (Optional[int]):  Example: 3.0.
        diff_url (Optional[str]):  Example: https://github.com/octocat/Hello-World/pull/1347.diff.
        draft (Optional[bool]): Indicates whether the pull request is a draft.
        head (Optional[CreatePullResponseHead]):
        html_url (Optional[str]):  Example: https://github.com/octocat/Hello-World/pull/1347.
        id (Optional[int]): The output pull request ID. Example: 1.0.
        issue_url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-World/issues/1347.
        labels (Optional[list['CreatePullResponseLabelsArrayItemRef']]):
        locked (Optional[bool]):  Example: True.
        maintainer_can_modify (Optional[bool]): Indicates whether maintainers can modify the pull request. Example:
                True.
        merge_commit_sha (Optional[str]):  Example: e5bd3914e2e596debea16f433f57875b5b90bcd6.
        mergeable (Optional[bool]):  Example: True.
        mergeable_state (Optional[str]):  Example: clean.
        merged (Optional[bool]):
        merged_at (Optional[datetime.datetime]):  Example: 2011-01-26T19:01:12.0000000+00:00.
        merged_by (Optional[CreatePullResponseMergedBy]):
        milestone (Optional[CreatePullResponseMilestone]):
        node_id (Optional[str]):  Example: MDExOlB1bGxSZXF1ZXN0MQ==.
        number (Optional[int]): Number uniquely identifying the pull request within its repository. Example: 42.0.
        patch_url (Optional[str]):  Example: https://github.com/octocat/Hello-World/pull/1347.patch.
        rebaseable (Optional[bool]):  Example: True.
        requested_reviewers (Optional[list['CreatePullResponseRequestedReviewersArrayItemRef']]):
        requested_teams (Optional[list['CreatePullResponseRequestedTeamsArrayItemRef']]):
        review_comment_url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-
                World/pulls/comments{/number}.
        review_comments (Optional[int]):  Example: 0.0.
        review_comments_url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-
                World/pulls/1347/comments.
        state (Optional[CreatePullResponseState]): State of this Pull Request. Either `open` or `closed`. Example: open.
        statuses_url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-
                World/statuses/6dcb09b5b57875f334f61aebed695e2e4193db5e.
        title (Optional[str]): The title of the new pull request. Required unless issue is specified. Example: Amazing
                new feature.
        updated_at (Optional[datetime.datetime]):  Example: 2011-01-26T19:01:12.0000000+00:00.
        url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-World/pulls/1347.
        user (Optional[CreatePullResponseUser]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    field_links: Optional["CreatePullResponseLinks"] = Field(
        alias="_links", default=None
    )
    active_lock_reason: Optional[str] = Field(alias="active_lock_reason", default=None)
    additions: Optional[int] = Field(alias="additions", default=None)
    assignee: Optional["CreatePullResponseAssignee"] = Field(
        alias="assignee", default=None
    )
    assignees: Optional[list["CreatePullResponseAssigneesArrayItemRef"]] = Field(
        alias="assignees", default=None
    )
    author_association: Optional[CreatePullResponseAuthorAssociation] = Field(
        alias="author_association", default=None
    )
    auto_merge: Optional["CreatePullResponseAutoMerge"] = Field(
        alias="auto_merge", default=None
    )
    base: Optional["CreatePullResponseBase"] = Field(alias="base", default=None)
    body: Optional[str] = Field(alias="body", default=None)
    changed_files: Optional[int] = Field(alias="changed_files", default=None)
    closed_at: Optional[datetime.datetime] = Field(alias="closed_at", default=None)
    comments: Optional[int] = Field(alias="comments", default=None)
    comments_url: Optional[str] = Field(alias="comments_url", default=None)
    commits: Optional[int] = Field(alias="commits", default=None)
    commits_url: Optional[str] = Field(alias="commits_url", default=None)
    created_at: Optional[datetime.datetime] = Field(alias="created_at", default=None)
    deletions: Optional[int] = Field(alias="deletions", default=None)
    diff_url: Optional[str] = Field(alias="diff_url", default=None)
    draft: Optional[bool] = Field(alias="draft", default=None)
    head: Optional["CreatePullResponseHead"] = Field(alias="head", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    issue_url: Optional[str] = Field(alias="issue_url", default=None)
    labels: Optional[list["CreatePullResponseLabelsArrayItemRef"]] = Field(
        alias="labels", default=None
    )
    locked: Optional[bool] = Field(alias="locked", default=None)
    maintainer_can_modify: Optional[bool] = Field(
        alias="maintainer_can_modify", default=None
    )
    merge_commit_sha: Optional[str] = Field(alias="merge_commit_sha", default=None)
    mergeable: Optional[bool] = Field(alias="mergeable", default=None)
    mergeable_state: Optional[str] = Field(alias="mergeable_state", default=None)
    merged: Optional[bool] = Field(alias="merged", default=None)
    merged_at: Optional[datetime.datetime] = Field(alias="merged_at", default=None)
    merged_by: Optional["CreatePullResponseMergedBy"] = Field(
        alias="merged_by", default=None
    )
    milestone: Optional["CreatePullResponseMilestone"] = Field(
        alias="milestone", default=None
    )
    node_id: Optional[str] = Field(alias="node_id", default=None)
    number: Optional[int] = Field(alias="number", default=None)
    patch_url: Optional[str] = Field(alias="patch_url", default=None)
    rebaseable: Optional[bool] = Field(alias="rebaseable", default=None)
    requested_reviewers: Optional[
        list["CreatePullResponseRequestedReviewersArrayItemRef"]
    ] = Field(alias="requested_reviewers", default=None)
    requested_teams: Optional[list["CreatePullResponseRequestedTeamsArrayItemRef"]] = (
        Field(alias="requested_teams", default=None)
    )
    review_comment_url: Optional[str] = Field(alias="review_comment_url", default=None)
    review_comments: Optional[int] = Field(alias="review_comments", default=None)
    review_comments_url: Optional[str] = Field(
        alias="review_comments_url", default=None
    )
    state: Optional[CreatePullResponseState] = Field(alias="state", default=None)
    statuses_url: Optional[str] = Field(alias="statuses_url", default=None)
    title: Optional[str] = Field(alias="title", default=None)
    updated_at: Optional[datetime.datetime] = Field(alias="updated_at", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    user: Optional["CreatePullResponseUser"] = Field(alias="user", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreatePullResponse"], src_dict: Dict[str, Any]):
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
