from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_all_branches_object import ListAllBranchesObject


class ListAllBranches(BaseModel):
    """
    Attributes:
        name (Optional[str]):  Example: "newbranch".
        node_id (Optional[str]):
        object_ (Optional[ListAllBranchesObject]):
        ref (Optional[str]): Name of the branch. Name cannot have wildcard characters (“ref/heads/master”)
        sha (Optional[str]): The SHA1 value for this reference
        url (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: Optional[str] = Field(alias="name", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    object_: Optional["ListAllBranchesObject"] = Field(alias="object", default=None)
    ref: Optional[str] = Field(alias="ref", default=None)
    sha: Optional[str] = Field(alias="sha", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListAllBranches"], src_dict: Dict[str, Any]):
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
