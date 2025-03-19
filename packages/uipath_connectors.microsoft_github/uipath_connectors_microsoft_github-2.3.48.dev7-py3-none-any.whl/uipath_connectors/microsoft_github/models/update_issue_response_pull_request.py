from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class UpdateIssueResponsePullRequest(BaseModel):
    """
    Attributes:
        diff_url (Optional[str]):
        html_url (Optional[str]):
        merged_at (Optional[datetime.datetime]):
        patch_url (Optional[str]):
        url (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    diff_url: Optional[str] = Field(alias="diff_url", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    merged_at: Optional[datetime.datetime] = Field(alias="merged_at", default=None)
    patch_url: Optional[str] = Field(alias="patch_url", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["UpdateIssueResponsePullRequest"], src_dict: Dict[str, Any]
    ):
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
