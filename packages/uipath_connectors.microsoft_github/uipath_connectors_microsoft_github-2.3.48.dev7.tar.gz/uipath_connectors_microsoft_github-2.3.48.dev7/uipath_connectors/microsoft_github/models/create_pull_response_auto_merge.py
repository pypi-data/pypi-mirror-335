from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_pull_response_auto_merge_auto_merge_method import (
    CreatePullResponseAutoMergeAutoMergeMethod,
)
from ..models.create_pull_response_auto_merge_enabled_by import (
    CreatePullResponseAutoMergeEnabledBy,
)


class CreatePullResponseAutoMerge(BaseModel):
    """
    Attributes:
        commit_message (Optional[str]): Commit message for the merge commit.
        commit_title (Optional[str]): Title for the merge commit message.
        enabled_by (Optional[CreatePullResponseAutoMergeEnabledBy]):
        merge_method (Optional[CreatePullResponseAutoMergeAutoMergeMethod]): The merge method to use.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    commit_message: Optional[str] = Field(alias="commit_message", default=None)
    commit_title: Optional[str] = Field(alias="commit_title", default=None)
    enabled_by: Optional["CreatePullResponseAutoMergeEnabledBy"] = Field(
        alias="enabled_by", default=None
    )
    merge_method: Optional[CreatePullResponseAutoMergeAutoMergeMethod] = Field(
        alias="merge_method", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreatePullResponseAutoMerge"], src_dict: Dict[str, Any]):
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
