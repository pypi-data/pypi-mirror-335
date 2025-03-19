from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_pull_response_milestone_milestone_state import (
    CreatePullResponseMilestoneMilestoneState,
)
import datetime
from ..models.create_pull_response_milestone_creator import (
    CreatePullResponseMilestoneCreator,
)


class CreatePullResponseMilestone(BaseModel):
    """
    Attributes:
        closed_at (Optional[datetime.datetime]):  Example: 2013-02-12T13:22:01.0000000+00:00.
        closed_issues (Optional[int]):  Example: 8.0.
        created_at (Optional[datetime.datetime]):  Example: 2011-04-10T20:09:31.0000000+00:00.
        creator (Optional[CreatePullResponseMilestoneCreator]):
        description (Optional[str]):  Example: Tracking milestone for version 1.0.
        due_on (Optional[datetime.datetime]):  Example: 2012-10-09T23:39:01.0000000+00:00.
        html_url (Optional[str]):  Example: https://github.com/octocat/Hello-World/milestones/v1.0.
        id (Optional[int]):  Example: 1002604.0.
        labels_url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-World/milestones/1/labels.
        node_id (Optional[str]):  Example: MDk6TWlsZXN0b25lMTAwMjYwNA==.
        number (Optional[int]): The number of the milestone. Example: 42.0.
        open_issues (Optional[int]):  Example: 4.0.
        state (Optional[CreatePullResponseMilestoneMilestoneState]): The state of the milestone. Example: open.
        title (Optional[str]): The title of the milestone. Example: v1.0.
        updated_at (Optional[datetime.datetime]):  Example: 2014-03-03T18:58:10.0000000+00:00.
        url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-World/milestones/1.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    closed_at: Optional[datetime.datetime] = Field(alias="closed_at", default=None)
    closed_issues: Optional[int] = Field(alias="closed_issues", default=None)
    created_at: Optional[datetime.datetime] = Field(alias="created_at", default=None)
    creator: Optional["CreatePullResponseMilestoneCreator"] = Field(
        alias="creator", default=None
    )
    description: Optional[str] = Field(alias="description", default=None)
    due_on: Optional[datetime.datetime] = Field(alias="due_on", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    labels_url: Optional[str] = Field(alias="labels_url", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    number: Optional[int] = Field(alias="number", default=None)
    open_issues: Optional[int] = Field(alias="open_issues", default=None)
    state: Optional[CreatePullResponseMilestoneMilestoneState] = Field(
        alias="state", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)
    updated_at: Optional[datetime.datetime] = Field(alias="updated_at", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreatePullResponseMilestone"], src_dict: Dict[str, Any]):
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
