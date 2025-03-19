from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_pull_request_head import CreatePullRequestHead
from ..models.create_pull_request_base import CreatePullRequestBase


class CreatePullRequest(BaseModel):
    """
    Attributes:
        base (Optional[CreatePullRequestBase]):
        body (Optional[str]): The contents of the pull request Example: Please pull these awesome changes.
        draft (Optional[bool]): Indicates whether the pull request is a draft.
        head (Optional[CreatePullRequestHead]):
        issue (Optional[int]): An issue in the repository to convert to a pull request. The issue title, body, and
                comments will become the title, body, and comments on the new pull request. Required unless title is specified.
                Example: 1.0.
        maintainer_can_modify (Optional[bool]): Indicates whether maintainers can modify the pull request. Example:
                True.
        title (Optional[str]): The title of the new pull request. Required unless issue is specified. Example: Amazing
                new feature.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    base: Optional["CreatePullRequestBase"] = Field(alias="base", default=None)
    body: Optional[str] = Field(alias="body", default=None)
    draft: Optional[bool] = Field(alias="draft", default=None)
    head: Optional["CreatePullRequestHead"] = Field(alias="head", default=None)
    issue: Optional[int] = Field(alias="issue", default=None)
    maintainer_can_modify: Optional[bool] = Field(
        alias="maintainer_can_modify", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreatePullRequest"], src_dict: Dict[str, Any]):
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
