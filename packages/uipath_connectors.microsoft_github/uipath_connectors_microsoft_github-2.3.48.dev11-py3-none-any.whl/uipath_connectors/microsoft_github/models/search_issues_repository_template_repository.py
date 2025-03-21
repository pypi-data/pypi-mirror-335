from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_issues_repository_template_repository_owner import (
    SearchIssuesRepositoryTemplateRepositoryOwner,
)
from ..models.search_issues_repository_template_repository_permissions import (
    SearchIssuesRepositoryTemplateRepositoryPermissions,
)


class SearchIssuesRepositoryTemplateRepository(BaseModel):
    """
    Attributes:
        allow_auto_merge (Optional[bool]):
        allow_merge_commit (Optional[bool]):
        allow_rebase_merge (Optional[bool]):
        allow_squash_merge (Optional[bool]):
        allow_update_branch (Optional[bool]):
        archive_url (Optional[str]):
        archived (Optional[bool]):
        assignees_url (Optional[str]):
        blobs_url (Optional[str]):
        branches_url (Optional[str]):
        clone_url (Optional[str]):
        collaborators_url (Optional[str]):
        comments_url (Optional[str]):
        commits_url (Optional[str]):
        compare_url (Optional[str]):
        contents_url (Optional[str]):
        contributors_url (Optional[str]):
        created_at (Optional[str]):
        default_branch (Optional[str]):
        delete_branch_on_merge (Optional[bool]):
        deployments_url (Optional[str]):
        description (Optional[str]):
        disabled (Optional[bool]):
        downloads_url (Optional[str]):
        events_url (Optional[str]):
        fork (Optional[bool]):
        forks_count (Optional[int]):
        forks_url (Optional[str]):
        full_name (Optional[str]):
        git_commits_url (Optional[str]):
        git_refs_url (Optional[str]):
        git_tags_url (Optional[str]):
        git_url (Optional[str]):
        has_downloads (Optional[bool]):
        has_issues (Optional[bool]):
        has_pages (Optional[bool]):
        has_projects (Optional[bool]):
        has_wiki (Optional[bool]):
        homepage (Optional[str]):
        hooks_url (Optional[str]):
        html_url (Optional[str]):
        id (Optional[int]):
        is_template (Optional[bool]):
        issue_comment_url (Optional[str]):
        issue_events_url (Optional[str]):
        issues_url (Optional[str]):
        keys_url (Optional[str]):
        labels_url (Optional[str]):
        language (Optional[str]):
        languages_url (Optional[str]):
        merges_url (Optional[str]):
        milestones_url (Optional[str]):
        mirror_url (Optional[str]):
        name (Optional[str]):
        network_count (Optional[int]):
        node_id (Optional[str]):
        notifications_url (Optional[str]):
        open_issues_count (Optional[int]):
        owner (Optional[SearchIssuesRepositoryTemplateRepositoryOwner]):
        permissions (Optional[SearchIssuesRepositoryTemplateRepositoryPermissions]):
        private (Optional[bool]):
        pulls_url (Optional[str]):
        pushed_at (Optional[str]):
        releases_url (Optional[str]):
        size (Optional[int]):
        ssh_url (Optional[str]):
        stargazers_count (Optional[int]):
        stargazers_url (Optional[str]):
        statuses_url (Optional[str]):
        subscribers_count (Optional[int]):
        subscribers_url (Optional[str]):
        subscription_url (Optional[str]):
        svn_url (Optional[str]):
        tags_url (Optional[str]):
        teams_url (Optional[str]):
        temp_clone_token (Optional[str]):
        topics (Optional[list[str]]):
        trees_url (Optional[str]):
        updated_at (Optional[str]):
        url (Optional[str]):
        use_squash_pr_title_as_default (Optional[bool]):
        visibility (Optional[str]):
        watchers_count (Optional[int]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_auto_merge: Optional[bool] = Field(alias="allow_auto_merge", default=None)
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
    created_at: Optional[str] = Field(alias="created_at", default=None)
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
    merges_url: Optional[str] = Field(alias="merges_url", default=None)
    milestones_url: Optional[str] = Field(alias="milestones_url", default=None)
    mirror_url: Optional[str] = Field(alias="mirror_url", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    network_count: Optional[int] = Field(alias="network_count", default=None)
    node_id: Optional[str] = Field(alias="node_id", default=None)
    notifications_url: Optional[str] = Field(alias="notifications_url", default=None)
    open_issues_count: Optional[int] = Field(alias="open_issues_count", default=None)
    owner: Optional["SearchIssuesRepositoryTemplateRepositoryOwner"] = Field(
        alias="owner", default=None
    )
    permissions: Optional["SearchIssuesRepositoryTemplateRepositoryPermissions"] = (
        Field(alias="permissions", default=None)
    )
    private: Optional[bool] = Field(alias="private", default=None)
    pulls_url: Optional[str] = Field(alias="pulls_url", default=None)
    pushed_at: Optional[str] = Field(alias="pushed_at", default=None)
    releases_url: Optional[str] = Field(alias="releases_url", default=None)
    size: Optional[int] = Field(alias="size", default=None)
    ssh_url: Optional[str] = Field(alias="ssh_url", default=None)
    stargazers_count: Optional[int] = Field(alias="stargazers_count", default=None)
    stargazers_url: Optional[str] = Field(alias="stargazers_url", default=None)
    statuses_url: Optional[str] = Field(alias="statuses_url", default=None)
    subscribers_count: Optional[int] = Field(alias="subscribers_count", default=None)
    subscribers_url: Optional[str] = Field(alias="subscribers_url", default=None)
    subscription_url: Optional[str] = Field(alias="subscription_url", default=None)
    svn_url: Optional[str] = Field(alias="svn_url", default=None)
    tags_url: Optional[str] = Field(alias="tags_url", default=None)
    teams_url: Optional[str] = Field(alias="teams_url", default=None)
    temp_clone_token: Optional[str] = Field(alias="temp_clone_token", default=None)
    topics: Optional[list[str]] = Field(alias="topics", default=None)
    trees_url: Optional[str] = Field(alias="trees_url", default=None)
    updated_at: Optional[str] = Field(alias="updated_at", default=None)
    url: Optional[str] = Field(alias="url", default=None)
    use_squash_pr_title_as_default: Optional[bool] = Field(
        alias="use_squash_pr_title_as_default", default=None
    )
    visibility: Optional[str] = Field(alias="visibility", default=None)
    watchers_count: Optional[int] = Field(alias="watchers_count", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchIssuesRepositoryTemplateRepository"], src_dict: Dict[str, Any]
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
