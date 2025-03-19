from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_pull_response_head_user import CreatePullResponseHeadUser
from ..models.create_pull_response_head_repo import CreatePullResponseHeadRepo


class CreatePullResponseHead(BaseModel):
    """
    Attributes:
        label (Optional[str]):
        ref (Optional[str]): The name of the branch where your changes are implemented. For cross-repository pull
                requests in the same network, namespace head with a user like this: username:branch.
        repo (Optional[CreatePullResponseHeadRepo]):
        sha (Optional[str]):
        user (Optional[CreatePullResponseHeadUser]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    label: Optional[str] = Field(alias="label", default=None)
    ref: Optional[str] = Field(alias="ref", default=None)
    repo: Optional["CreatePullResponseHeadRepo"] = Field(alias="repo", default=None)
    sha: Optional[str] = Field(alias="sha", default=None)
    user: Optional["CreatePullResponseHeadUser"] = Field(alias="user", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreatePullResponseHead"], src_dict: Dict[str, Any]):
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
