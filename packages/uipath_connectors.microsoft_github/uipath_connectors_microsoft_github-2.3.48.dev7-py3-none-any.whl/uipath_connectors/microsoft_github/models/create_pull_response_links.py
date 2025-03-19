from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_pull_response_links_html import CreatePullResponseLinksHtml
from ..models.create_pull_response_links_review_comment import (
    CreatePullResponseLinksReviewComment,
)
from ..models.create_pull_response_links_commits import CreatePullResponseLinksCommits
from ..models.create_pull_response_links_review_comments import (
    CreatePullResponseLinksReviewComments,
)
from ..models.create_pull_response_links_issue import CreatePullResponseLinksIssue
from ..models.create_pull_response_links_comments import CreatePullResponseLinksComments
from ..models.create_pull_response_links_statuses import CreatePullResponseLinksStatuses
from ..models.create_pull_response_links_self import CreatePullResponseLinksSelf


class CreatePullResponseLinks(BaseModel):
    """
    Attributes:
        comments (Optional[CreatePullResponseLinksComments]):
        commits (Optional[CreatePullResponseLinksCommits]):
        html (Optional[CreatePullResponseLinksHtml]):
        issue (Optional[CreatePullResponseLinksIssue]):
        review_comment (Optional[CreatePullResponseLinksReviewComment]):
        review_comments (Optional[CreatePullResponseLinksReviewComments]):
        self_ (Optional[CreatePullResponseLinksSelf]):
        statuses (Optional[CreatePullResponseLinksStatuses]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    comments: Optional["CreatePullResponseLinksComments"] = Field(
        alias="comments", default=None
    )
    commits: Optional["CreatePullResponseLinksCommits"] = Field(
        alias="commits", default=None
    )
    html: Optional["CreatePullResponseLinksHtml"] = Field(alias="html", default=None)
    issue: Optional["CreatePullResponseLinksIssue"] = Field(alias="issue", default=None)
    review_comment: Optional["CreatePullResponseLinksReviewComment"] = Field(
        alias="review_comment", default=None
    )
    review_comments: Optional["CreatePullResponseLinksReviewComments"] = Field(
        alias="review_comments", default=None
    )
    self_: Optional["CreatePullResponseLinksSelf"] = Field(alias="self", default=None)
    statuses: Optional["CreatePullResponseLinksStatuses"] = Field(
        alias="statuses", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreatePullResponseLinks"], src_dict: Dict[str, Any]):
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
