from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreateRepoResponseLicense(BaseModel):
    """
    Attributes:
        html_url (Optional[str]):
        key (Optional[str]):  Example: mit.
        name (Optional[str]):  Example: MIT License.
        node_id (Optional[str]):  Example: MDc6TGljZW5zZW1pdA==.
        spdx_id (Optional[str]):  Example: MIT.
        url (Optional[str]):  Example: https://api.github.com/licenses/mit.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    html_url: Optional[str] = Field(alias="html_url", default=None)
    key: Optional[str] = Field(alias="key", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    spdx_id: Optional[str] = Field(alias="spdx_id", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateRepoResponseLicense"], src_dict: Dict[str, Any]):
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
