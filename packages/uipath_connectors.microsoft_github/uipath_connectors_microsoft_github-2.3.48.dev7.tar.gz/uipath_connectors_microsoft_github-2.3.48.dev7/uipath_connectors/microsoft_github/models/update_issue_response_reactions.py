from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class UpdateIssueResponseReactions(BaseModel):
    """
    Attributes:
        field_1 (Optional[int]):
        field__1 (Optional[int]):
        confused (Optional[int]):
        eyes (Optional[int]):
        heart (Optional[int]):
        hooray (Optional[int]):
        laugh (Optional[int]):
        rocket (Optional[int]):
        total_count (Optional[int]):
        url (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    field_1: Optional[int] = Field(alias="+1", default=None)
    field__1: Optional[int] = Field(alias="-1", default=None)
    confused: Optional[int] = Field(alias="confused", default=None)
    eyes: Optional[int] = Field(alias="eyes", default=None)
    heart: Optional[int] = Field(alias="heart", default=None)
    hooray: Optional[int] = Field(alias="hooray", default=None)
    laugh: Optional[int] = Field(alias="laugh", default=None)
    rocket: Optional[int] = Field(alias="rocket", default=None)
    total_count: Optional[int] = Field(alias="total_count", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateIssueResponseReactions"], src_dict: Dict[str, Any]):
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
