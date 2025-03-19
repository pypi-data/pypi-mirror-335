from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type


class CreatePullResponseRequestedTeamsArrayItemRef(BaseModel):
    """
    Attributes:
        description (Optional[str]): Description of the team Example: A great team..
        html_url (Optional[str]):  Example: https://github.com/orgs/rails/teams/core.
        id (Optional[int]): Unique identifier of the team Example: 1.0.
        ldap_dn (Optional[str]): Distinguished Name (DN) that team maps to within LDAP environment Example:
                uid=example,ou=users,dc=github,dc=com.
        members_url (Optional[str]):  Example: https://api.github.com/organizations/1/team/1/members{/member}.
        name (Optional[str]): Name of the team Example: Justice League.
        node_id (Optional[str]):  Example: MDQ6VGVhbTE=.
        permission (Optional[str]): Permission that the team will have for its repositories Example: admin.
        privacy (Optional[str]): The level of privacy this team should have Example: closed.
        repositories_url (Optional[str]):  Example: https://api.github.com/organizations/1/team/1/repos.
        slug (Optional[str]):  Example: justice-league.
        url (Optional[str]): URL for the team Example: https://api.github.com/organizations/1/team/1.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    description: Optional[str] = Field(alias="description", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    ldap_dn: Optional[str] = Field(alias="ldap_dn", default=None)
    members_url: Optional[str] = Field(alias="members_url", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    permission: Optional[str] = Field(alias="permission", default=None)
    privacy: Optional[str] = Field(alias="privacy", default=None)
    repositories_url: Optional[str] = Field(alias="repositories_url", default=None)
    slug: Optional[str] = Field(alias="slug", default=None)
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["CreatePullResponseRequestedTeamsArrayItemRef"],
        src_dict: Dict[str, Any],
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
