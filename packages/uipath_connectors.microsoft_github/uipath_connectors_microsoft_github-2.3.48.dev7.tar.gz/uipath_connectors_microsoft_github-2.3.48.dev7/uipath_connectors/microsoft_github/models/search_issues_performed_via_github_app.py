from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime
from ..models.search_issues_performed_via_github_app_owner import (
    SearchIssuesPerformedViaGithubAppOwner,
)
from ..models.search_issues_performed_via_github_app_permissions import (
    SearchIssuesPerformedViaGithubAppPermissions,
)


class SearchIssuesPerformedViaGithubApp(BaseModel):
    r"""
    Attributes:
        client_id (Optional[str]):  Example: "Iv1.25b5d1e65ffc4022".
        client_secret (Optional[str]):  Example: "1d4b2097ac622ba702d19de498f005747a8b21d3".
        created_at (Optional[datetime.datetime]):  Example: 2017-07-09T01:48:44.0000000+05:30.
        description (Optional[str]):  Example: The description of the app..
        events (Optional[list[str]]):
        external_url (Optional[str]):  Example: https://example.com.
        html_url (Optional[str]):  Example: https://github.com/apps/super-ci.
        id (Optional[int]): Unique identifier of the GitHub app Example: 37.0.
        installations_count (Optional[int]): The number of installations associated with the GitHub app Example: 5.0.
        name (Optional[str]): The name of the GitHub app Example: Probot Owners.
        node_id (Optional[str]):  Example: MDExOkludGVncmF0aW9uMQ==.
        owner (Optional[SearchIssuesPerformedViaGithubAppOwner]):
        pem (Optional[str]):  Example: "-----BEGIN RSA PRIVATE KEY-----
                \nMIIEogIBAAKCAQEArYxrNYD/iT5CZVpRJu4rBKmmze3PVmT/gCo2ATUvDvZTPTey\nxcGJ3vvrJXazKk06pN05TN29o98jrYz4cengG3YGsXPN
                EpKsIrEl8NhbnxapEnM9\nJCMRe0P5JcPsfZlX6hmiT7136GRWiGOUba2X9+HKh8QJVLG5rM007TBER9/z9mWm\nrJuNh+m5l320oBQY/Qq3A7wz
                dEfZw8qm/mIN0FCeoXH1L6B8xXWaAYBwhTEh6SSn\nZHlO1Xu1JWDmAvBCi0RO5aRSKM8q9QEkvvHP4yweAtK3N8+aAbZ7ovaDhyGz8r6r\nzhU1
                b8Uo0Z2ysf503WqzQgIajr7Fry7/kUwpgQIDAQABAoIBADwJp80Ko1xHPZDy\nfcCKBDfIuPvkmSW6KumbsLMaQv1aGdHDwwTGv3t0ixSay8CGlx
                MRtRDyZPib6SvQ\n6OH/lpfpbMdW2ErkksgtoIKBVrDilfrcAvrNZu7NxRNbhCSvN8q0s4ICecjbbVQh\nnueSdlA6vGXbW58BHMq68uRbHkP+k+
                mM9U0mDJ1HMch67wlg5GbayVRt63H7R2+r\nVxcna7B80J/lCEjIYZznawgiTvp3MSanTglqAYi+m1EcSsP14bJIB9vgaxS79kTu\noiSo93leJb
                BvuGo8QEiUqTwMw4tDksmkLsoqNKQ1q9P7LZ9DGcujtPy4EZsamSJT\ny8OJt0ECgYEA2lxOxJsQk2kI325JgKFjo92mQeUObIvPfSNWUIZQDTjn
                iOI6Gv63\nGLWVFrZcvQBWjMEQraJA9xjPbblV8PtfO87MiJGLWCHFxmPz2dzoedN+2Coxom8m\nV95CLz8QUShuao6u/RYcvUaZEoYs5bHcTmy5
                sBK80JyEmafJPtCQVxMCgYEAy3ar\nZr3yv4xRPEPMat4rseswmuMooSaK3SKub19WFI5IAtB/e7qR1Rj9JhOGcZz+OQrl\nT78O2OFYlgOIkJPv
                RMrPpK5V9lslc7tz1FSh3BZMRGq5jSyD7ETSOQ0c8T2O/s7v\nbeEPbVbDe4mwvM24XByH0GnWveVxaDl51ABD65sCgYB3ZAspUkOA5egVCh8kNp
                nd\nSd6SnuQBE3ySRlT2WEnCwP9Ph6oPgn+oAfiPX4xbRqkL8q/k0BdHQ4h+zNwhk7+h\nWtPYRAP1Xxnc/F+jGjb+DVaIaKGU18MWPg7f+FI6na
                mpl3Q0KvfxwX0GdNhtio8T\nTj1E+SnFwh56SRQuxSh2gwKBgHKjlIO5NtNSflsUYFM+hyQiPiqnHzddfhSG+/3o\nm5nNaSmczJesUYreH5San7
                /YEy2UxAugvP7aSY2MxB+iGsiJ9WD2kZzTUlDZJ7RV\nUzWsoqBR+eZfVJ2FUWWvy8TpSG6trh4dFxImNtKejCR1TREpSiTV3Zb1dmahK9GV\nrK
                9NAoGAbBxRLoC01xfxCTgt5BDiBcFVh4fp5yYKwavJPLzHSpuDOrrI9jDn1oKN\nonq5sDU1i391zfQvdrbX4Ova48BN+B7p63FocP/MK5tyyBoT
                8zQEk2+vWDOw7H/Z\nu5dTCPxTIsoIwUw1I+7yIxqJzLPFgR2gVBwY1ra/8iAqCj+zeBw=\n-----END RSA PRIVATE KEY-----\n".
        permissions (Optional[SearchIssuesPerformedViaGithubAppPermissions]):
        slug (Optional[str]): The slug name of the GitHub app Example: probot-owners.
        updated_at (Optional[datetime.datetime]):  Example: 2017-07-09T01:48:44.0000000+05:30.
        webhook_secret (Optional[str]):  Example: "6fba8f2fc8a7e8f2cca5577eddd82ca7586b3b6b".
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    client_id: Optional[str] = Field(alias="client_id", default=None)
    client_secret: Optional[str] = Field(alias="client_secret", default=None)
    created_at: Optional[datetime.datetime] = Field(alias="created_at", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    events: Optional[list[str]] = Field(alias="events", default=None)
    external_url: Optional[str] = Field(alias="external_url", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    installations_count: Optional[int] = Field(
        alias="installations_count", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    owner: Optional["SearchIssuesPerformedViaGithubAppOwner"] = Field(
        alias="owner", default=None
    )
    pem: Optional[str] = Field(alias="pem", default=None)
    permissions: Optional["SearchIssuesPerformedViaGithubAppPermissions"] = Field(
        alias="permissions", default=None
    )
    slug: Optional[str] = Field(alias="slug", default=None)
    updated_at: Optional[datetime.datetime] = Field(alias="updated_at", default=None)
    webhook_secret: Optional[str] = Field(alias="webhook_secret", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchIssuesPerformedViaGithubApp"], src_dict: Dict[str, Any]
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
