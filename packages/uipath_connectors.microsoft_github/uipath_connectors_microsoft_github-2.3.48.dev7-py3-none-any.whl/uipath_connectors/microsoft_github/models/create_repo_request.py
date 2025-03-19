from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_repo_request_visibility import CreateRepoRequestVisibility


class CreateRepoRequest(BaseModel):
    """
    Attributes:
        name (str): The name of the repository. The name is not case sensitive. Example: Hello-World.
        allow_auto_merge (Optional[bool]):  Either true to allow auto-merge on pull requests, or false to disallow auto-
                merge
        allow_merge_commit (Optional[bool]): Either `true` to allow merging pull requests with a merge commit, or
                `false` to prevent merging pull requests with merge commits. Example: True.
        allow_rebase_merge (Optional[bool]): Either `true` to allow rebase-merging pull requests, or `false` to prevent
                rebase-merging. Example: True.
        allow_squash_merge (Optional[bool]): Either `true` to allow squash-merging pull requests, or `false` to prevent
                squash-merging. Example: True.
        auto_init (Optional[bool]): Pass true to create an initial commit with empty README
        delete_branch_on_merge (Optional[bool]): Either true to allow automatically deleting head branches when pull
                requests are merged, or false to prevent automatic deletion. The authenticated user must be an organization
                owner to set this property to true.
        description (Optional[str]): A short description of the repository Example: This your first repo!.
        gitignore_template (Optional[str]): Desired language or platform .gitignore template to apply. Use the name of
                the template without the extension. For example, "Haskell".
        has_issues (Optional[bool]): Either `true` to enable issues for this repository or `false` to disable them.
                Example: True.
        has_projects (Optional[bool]): Either `true` to enable projects for this repository or `false` to disable them.
                **Note:** If you're creating a repository in an organization that has disabled repository projects, the default
                is `false`, and if you pass `true`, the API returns an error. Example: True.
        has_wiki (Optional[bool]): Either `true` to enable the wiki for this repository or `false` to disable it.
                Example: True.
        homepage (Optional[str]): A URL with more information about the repository Example: https://github.com.
        is_template (Optional[bool]): Either true to make this repo available as a template repository or false to
                prevent it Example: True.
        license_template (Optional[str]): Choose an open source license template that best suits your needs, and then
                use the license keyword as the license_template string. For example, "mit" or "mpl-2.0".
        private (Optional[bool]): Either true to make the repository private or false to make it public
        team_id (Optional[int]): The ID of the team that will be granted access to this repository. This is only valid
                when creating a repository in an organization.
        use_squash_pr_title_as_default (Optional[bool]): Either `true` to allow squash-merge commits to use pull request
                title, or `false` to use commit message.
        visibility (Optional[CreateRepoRequestVisibility]): Can be public, private or internal. Example: public.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    name: str = Field(alias="name")
    allow_auto_merge: Optional[bool] = Field(alias="allow_auto_merge", default=None)
    allow_merge_commit: Optional[bool] = Field(alias="allow_merge_commit", default=None)
    allow_rebase_merge: Optional[bool] = Field(alias="allow_rebase_merge", default=None)
    allow_squash_merge: Optional[bool] = Field(alias="allow_squash_merge", default=None)
    auto_init: Optional[bool] = Field(alias="auto_init", default=None)
    delete_branch_on_merge: Optional[bool] = Field(
        alias="delete_branch_on_merge", default=None
    )
    description: Optional[str] = Field(alias="description", default=None)
    gitignore_template: Optional[str] = Field(alias="gitignore_template", default=None)
    has_issues: Optional[bool] = Field(alias="has_issues", default=None)
    has_projects: Optional[bool] = Field(alias="has_projects", default=None)
    has_wiki: Optional[bool] = Field(alias="has_wiki", default=None)
    homepage: Optional[str] = Field(alias="homepage", default=None)
    is_template: Optional[bool] = Field(alias="is_template", default=None)
    license_template: Optional[str] = Field(alias="license_template", default=None)
    private: Optional[bool] = Field(alias="private", default=None)
    team_id: Optional[int] = Field(alias="team_id", default=None)
    use_squash_pr_title_as_default: Optional[bool] = Field(
        alias="use_squash_pr_title_as_default", default=None
    )
    visibility: Optional[CreateRepoRequestVisibility] = Field(
        alias="visibility", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateRepoRequest"], src_dict: Dict[str, Any]):
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
