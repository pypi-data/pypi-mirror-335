from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreatePullResponseHeadRepoOwner(BaseModel):
    """
    Attributes:
        avatar_url (Optional[str]):  Example: https://github.com/images/error/octocat_happy.gif.
        events_url (Optional[str]):  Example: https://api.github.com/users/octocat/events{/privacy}.
        followers_url (Optional[str]):  Example: https://api.github.com/users/octocat/followers.
        following_url (Optional[str]):  Example: https://api.github.com/users/octocat/following{/other_user}.
        gists_url (Optional[str]):  Example: https://api.github.com/users/octocat/gists{/gist_id}.
        gravatar_id (Optional[str]):  Example: 41d064eb2195891e12d0413f63227ea7.
        html_url (Optional[str]):  Example: https://github.com/octocat.
        id (Optional[int]):  Example: 1.0.
        login (Optional[str]):  Example: octocat.
        node_id (Optional[str]):  Example: MDQ6VXNlcjE=.
        organizations_url (Optional[str]):  Example: https://api.github.com/users/octocat/orgs.
        received_events_url (Optional[str]):  Example: https://api.github.com/users/octocat/received_events.
        repos_url (Optional[str]):  Example: https://api.github.com/users/octocat/repos.
        site_admin (Optional[bool]):
        starred_url (Optional[str]):  Example: https://api.github.com/users/octocat/starred{/owner}{/repo}.
        subscriptions_url (Optional[str]):  Example: https://api.github.com/users/octocat/subscriptions.
        type_ (Optional[str]):  Example: User.
        url (Optional[str]):  Example: https://api.github.com/users/octocat.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    avatar_url: Optional[str] = Field(alias="avatar_url", default=None)
    events_url: Optional[str] = Field(alias="events_url", default=None)
    followers_url: Optional[str] = Field(alias="followers_url", default=None)
    following_url: Optional[str] = Field(alias="following_url", default=None)
    gists_url: Optional[str] = Field(alias="gists_url", default=None)
    gravatar_id: Optional[str] = Field(alias="gravatar_id", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    login: Optional[str] = Field(alias="login", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    organizations_url: Optional[str] = Field(alias="organizations_url", default=None)
    received_events_url: Optional[str] = Field(
        alias="received_events_url", default=None
    )
    repos_url: Optional[str] = Field(alias="repos_url", default=None)
    site_admin: Optional[bool] = Field(alias="site_admin", default=None)
    starred_url: Optional[str] = Field(alias="starred_url", default=None)
    subscriptions_url: Optional[str] = Field(alias="subscriptions_url", default=None)
    type_: Optional[str] = Field(alias="type", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreatePullResponseHeadRepoOwner"], src_dict: Dict[str, Any]
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
