from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.merge_pull_request_merge_method import MergePullRequestMergeMethod


class MergePullRequest(BaseModel):
    """
    Attributes:
        commit_message (Optional[str]): Extra detail to append to automatic commit message
        commit_title (Optional[str]): Title for the automatic commit message
        merge_method (Optional[MergePullRequestMergeMethod]): The merge method to use
        sha (Optional[str]): SHA that pull request head must match to allow merge
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    commit_message: Optional[str] = Field(alias="commit_message", default=None)
    commit_title: Optional[str] = Field(alias="commit_title", default=None)
    merge_method: Optional[MergePullRequestMergeMethod] = Field(
        alias="merge_method", default=None
    )
    sha: Optional[str] = Field(alias="sha", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["MergePullRequest"], src_dict: Dict[str, Any]):
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
