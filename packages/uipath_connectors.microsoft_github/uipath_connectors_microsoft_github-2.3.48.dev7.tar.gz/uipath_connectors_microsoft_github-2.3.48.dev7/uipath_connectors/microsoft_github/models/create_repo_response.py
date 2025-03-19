from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_repo_response_visibility import CreateRepoResponseVisibility
import datetime
from ..models.create_repo_response_owner import CreateRepoResponseOwner
from ..models.create_repo_response_permissions import CreateRepoResponsePermissions
from ..models.create_repo_response_organization import CreateRepoResponseOrganization
from ..models.create_repo_response_license import CreateRepoResponseLicense
from ..models.create_repo_response_template_repository import (
    CreateRepoResponseTemplateRepository,
)


class CreateRepoResponse(BaseModel):
    """
    Attributes:
        allow_auto_merge (Optional[bool]):  Either true to allow auto-merge on pull requests, or false to disallow auto-
                merge
        allow_forking (Optional[bool]): Either true to allow private forks, or false to prevent private forks. Default
                is false. Example: True.
        allow_merge_commit (Optional[bool]): Either `true` to allow merging pull requests with a merge commit, or
                `false` to prevent merging pull requests with merge commits. Example: True.
        allow_rebase_merge (Optional[bool]): Either `true` to allow rebase-merging pull requests, or `false` to prevent
                rebase-merging. Example: True.
        allow_squash_merge (Optional[bool]): Either `true` to allow squash-merging pull requests, or `false` to prevent
                squash-merging. Example: True.
        allow_update_branch (Optional[bool]): Either `true` to always allow a pull request head branch that is behind
                its base branch to be updated even if it is not required to be up to date before merging, or false otherwise.
                Example: True.
        archive_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/{archive_format}{/ref}.
        archived (Optional[bool]): Provide "true" to archive this repository. You cannot unarchive repositories through
                the API.
        assignees_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/assignees{/user}.
        blobs_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/git/blobs{/sha}.
        branches_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/branches{/branch}.
        clone_url (Optional[str]):  Example: https://github.com/octocat/Hello-World.git.
        collaborators_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-
                World/collaborators{/collaborator}.
        comments_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/comments{/number}.
        commits_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/commits{/sha}.
        compare_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/compare/{base}...{head}.
        contents_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/contents/{+path}.
        contributors_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/contributors.
        created_at (Optional[datetime.datetime]):  Example: 2011-01-26T19:01:12.0000000+00:00.
        default_branch (Optional[str]): Updates the default branch for this repository. Example: master.
        delete_branch_on_merge (Optional[bool]): Either true to allow automatically deleting head branches when pull
                requests are merged, or false to prevent automatic deletion. The authenticated user must be an organization
                owner to set this property to true.
        deployments_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/deployments.
        description (Optional[str]): A short description of the repository Example: This your first repo!.
        disabled (Optional[bool]): Returns whether or not this repository disabled.
        downloads_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/downloads.
        events_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/events.
        fork (Optional[bool]):
        forks (Optional[int]):
        forks_count (Optional[int]):  Example: 9.0.
        forks_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/forks.
        full_name (Optional[str]):  Example: octocat/Hello-World.
        git_commits_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/git/commits{/sha}.
        git_refs_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/git/refs{/sha}.
        git_tags_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/git/tags{/sha}.
        git_url (Optional[str]):  Example: git:github.com/octocat/Hello-World.git.
        has_downloads (Optional[bool]): Whether downloads are enabled. Example: True.
        has_issues (Optional[bool]): Either `true` to enable issues for this repository or `false` to disable them.
                Example: True.
        has_pages (Optional[bool]):
        has_projects (Optional[bool]): Either `true` to enable projects for this repository or `false` to disable them.
                **Note:** If you're creating a repository in an organization that has disabled repository projects, the default
                is `false`, and if you pass `true`, the API returns an error. Example: True.
        has_wiki (Optional[bool]): Either `true` to enable the wiki for this repository or `false` to disable it.
                Example: True.
        homepage (Optional[str]): A URL with more information about the repository Example: https://github.com.
        hooks_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/hooks.
        html_url (Optional[str]):  Example: https://github.com/octocat/Hello-World.
        id (Optional[int]): The output repository ID Example: 1296269.0.
        is_template (Optional[bool]): Either true to make this repo available as a template repository or false to
                prevent it Example: True.
        issue_comment_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-
                World/issues/comments{/number}.
        issue_events_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-
                World/issues/events{/number}.
        issues_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/issues{/number}.
        keys_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/keys{/key_id}.
        labels_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/labels{/name}.
        language (Optional[str]):
        languages_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/languages.
        license_ (Optional[CreateRepoResponseLicense]):
        master_branch (Optional[str]):
        merges_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/merges.
        milestones_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/milestones{/number}.
        mirror_url (Optional[str]):  Example: git:git.example.com/octocat/Hello-World.
        name (Optional[str]): The name of the repository. The name is not case sensitive. Example: Hello-World.
        network_count (Optional[int]):  Example: 0.0.
        node_id (Optional[str]):  Example: MDEwOlJlcG9zaXRvcnkxMjk2MjY5.
        notifications_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-
                World/notifications{?since,all,participating}.
        open_issues (Optional[int]):
        open_issues_count (Optional[int]):  Example: 0.0.
        organization (Optional[CreateRepoResponseOrganization]):
        owner (Optional[CreateRepoResponseOwner]):
        permissions (Optional[CreateRepoResponsePermissions]):
        private (Optional[bool]): Either true to make the repository private or false to make it public
        pulls_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/pulls{/number}.
        pushed_at (Optional[datetime.datetime]):  Example: 2011-01-26T19:06:43.0000000+00:00.
        releases_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/releases{/id}.
        size (Optional[int]):  Example: 108.0.
        ssh_url (Optional[str]):  Example: git@github.com:octocat/Hello-World.git.
        stargazers_count (Optional[int]):  Example: 80.0.
        stargazers_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/stargazers.
        starred_at (Optional[str]):  Example: "2020-07-09T00:17:42Z".
        statuses_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/statuses/{sha}.
        subscribers_count (Optional[int]):  Example: 42.0.
        subscribers_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/subscribers.
        subscription_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/subscription.
        svn_url (Optional[str]):  Example: https://svn.github.com/octocat/Hello-World.
        tags_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/tags.
        teams_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/teams.
        temp_clone_token (Optional[str]):
        template_repository (Optional[CreateRepoResponseTemplateRepository]):
        topics (Optional[list[str]]):
        trees_url (Optional[str]):  Example: http://api.github.com/repos/octocat/Hello-World/git/trees{/sha}.
        updated_at (Optional[datetime.datetime]):  Example: 2011-01-26T19:14:43.0000000+00:00.
        url (Optional[str]):  Example: https://api.github.com/repos/octocat/Hello-World.
        use_squash_pr_title_as_default (Optional[bool]): Either `true` to allow squash-merge commits to use pull request
                title, or `false` to use commit message.
        visibility (Optional[CreateRepoResponseVisibility]): Can be public, private or internal. Example: public.
        watchers (Optional[int]):
        watchers_count (Optional[int]):  Example: 80.0.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_auto_merge: Optional[bool] = Field(alias="allow_auto_merge", default=None)
    allow_forking: Optional[bool] = Field(alias="allow_forking", default=None)
    allow_merge_commit: Optional[bool] = Field(alias="allow_merge_commit", default=None)
    allow_rebase_merge: Optional[bool] = Field(alias="allow_rebase_merge", default=None)
    allow_squash_merge: Optional[bool] = Field(alias="allow_squash_merge", default=None)
    allow_update_branch: Optional[bool] = Field(
        alias="allow_update_branch", default=None
    )
    archive_url: Optional[str] = Field(alias="archive_url", default=None)
    archived: Optional[bool] = Field(alias="archived", default=None)
    assignees_url: Optional[str] = Field(alias="assignees_url", default=None)
    blobs_url: Optional[str] = Field(alias="blobs_url", default=None)
    branches_url: Optional[str] = Field(alias="branches_url", default=None)
    clone_url: Optional[str] = Field(alias="clone_url", default=None)
    collaborators_url: Optional[str] = Field(alias="collaborators_url", default=None)
    comments_url: Optional[str] = Field(alias="comments_url", default=None)
    commits_url: Optional[str] = Field(alias="commits_url", default=None)
    compare_url: Optional[str] = Field(alias="compare_url", default=None)
    contents_url: Optional[str] = Field(alias="contents_url", default=None)
    contributors_url: Optional[str] = Field(alias="contributors_url", default=None)
    created_at: Optional[datetime.datetime] = Field(alias="created_at", default=None)
    default_branch: Optional[str] = Field(alias="default_branch", default=None)
    delete_branch_on_merge: Optional[bool] = Field(
        alias="delete_branch_on_merge", default=None
    )
    deployments_url: Optional[str] = Field(alias="deployments_url", default=None)
    description: Optional[str] = Field(alias="description", default=None)
    disabled: Optional[bool] = Field(alias="disabled", default=None)
    downloads_url: Optional[str] = Field(alias="downloads_url", default=None)
    events_url: Optional[str] = Field(alias="events_url", default=None)
    fork: Optional[bool] = Field(alias="fork", default=None)
    forks: Optional[int] = Field(alias="forks", default=None)
    forks_count: Optional[int] = Field(alias="forks_count", default=None)
    forks_url: Optional[str] = Field(alias="forks_url", default=None)
    full_name: Optional[str] = Field(alias="full_name", default=None)
    git_commits_url: Optional[str] = Field(alias="git_commits_url", default=None)
    git_refs_url: Optional[str] = Field(alias="git_refs_url", default=None)
    git_tags_url: Optional[str] = Field(alias="git_tags_url", default=None)
    git_url: Optional[str] = Field(alias="git_url", default=None)
    has_downloads: Optional[bool] = Field(alias="has_downloads", default=None)
    has_issues: Optional[bool] = Field(alias="has_issues", default=None)
    has_pages: Optional[bool] = Field(alias="has_pages", default=None)
    has_projects: Optional[bool] = Field(alias="has_projects", default=None)
    has_wiki: Optional[bool] = Field(alias="has_wiki", default=None)
    homepage: Optional[str] = Field(alias="homepage", default=None)
    hooks_url: Optional[str] = Field(alias="hooks_url", default=None)
    html_url: Optional[str] = Field(alias="html_url", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    is_template: Optional[bool] = Field(alias="is_template", default=None)
    issue_comment_url: Optional[str] = Field(alias="issue_comment_url", default=None)
    issue_events_url: Optional[str] = Field(alias="issue_events_url", default=None)
    issues_url: Optional[str] = Field(alias="issues_url", default=None)
    keys_url: Optional[str] = Field(alias="keys_url", default=None)
    labels_url: Optional[str] = Field(alias="labels_url", default=None)
    language: Optional[str] = Field(alias="language", default=None)
    languages_url: Optional[str] = Field(alias="languages_url", default=None)
    license_: Optional["CreateRepoResponseLicense"] = Field(
        alias="license", default=None
    )
    master_branch: Optional[str] = Field(alias="master_branch", default=None)
    merges_url: Optional[str] = Field(alias="merges_url", default=None)
    milestones_url: Optional[str] = Field(alias="milestones_url", default=None)
    mirror_url: Optional[str] = Field(alias="mirror_url", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    network_count: Optional[int] = Field(alias="network_count", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    notifications_url: Optional[str] = Field(alias="notifications_url", default=None)
    open_issues: Optional[int] = Field(alias="open_issues", default=None)
    open_issues_count: Optional[int] = Field(alias="open_issues_count", default=None)
    organization: Optional["CreateRepoResponseOrganization"] = Field(
        alias="organization", default=None
    )
    owner: Optional["CreateRepoResponseOwner"] = Field(alias="owner", default=None)
    permissions: Optional["CreateRepoResponsePermissions"] = Field(
        alias="permissions", default=None
    )
    private: Optional[bool] = Field(alias="private", default=None)
    pulls_url: Optional[str] = Field(alias="pulls_url", default=None)
    pushed_at: Optional[datetime.datetime] = Field(alias="pushed_at", default=None)
    releases_url: Optional[str] = Field(alias="releases_url", default=None)
    size: Optional[int] = Field(alias="size", default=None)
    ssh_url: Optional[str] = Field(alias="ssh_url", default=None)
    stargazers_count: Optional[int] = Field(alias="stargazers_count", default=None)
    stargazers_url: Optional[str] = Field(alias="stargazers_url", default=None)
    starred_at: Optional[str] = Field(alias="starred_at", default=None)
    statuses_url: Optional[str] = Field(alias="statuses_url", default=None)
    subscribers_count: Optional[int] = Field(alias="subscribers_count", default=None)
    subscribers_url: Optional[str] = Field(alias="subscribers_url", default=None)
    subscription_url: Optional[str] = Field(alias="subscription_url", default=None)
    svn_url: Optional[str] = Field(alias="svn_url", default=None)
    tags_url: Optional[str] = Field(alias="tags_url", default=None)
    teams_url: Optional[str] = Field(alias="teams_url", default=None)
    temp_clone_token: Optional[str] = Field(alias="temp_clone_token", default=None)
    template_repository: Optional["CreateRepoResponseTemplateRepository"] = Field(
        alias="template_repository", default=None
    )
    topics: Optional[list[str]] = Field(alias="topics", default=None)
    trees_url: Optional[str] = Field(alias="trees_url", default=None)
    updated_at: Optional[datetime.datetime] = Field(alias="updated_at", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    use_squash_pr_title_as_default: Optional[bool] = Field(
        alias="use_squash_pr_title_as_default", default=None
    )
    visibility: Optional[CreateRepoResponseVisibility] = Field(
        alias="visibility", default=None
    )
    watchers: Optional[int] = Field(alias="watchers", default=None)
    watchers_count: Optional[int] = Field(alias="watchers_count", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateRepoResponse"], src_dict: Dict[str, Any]):
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
