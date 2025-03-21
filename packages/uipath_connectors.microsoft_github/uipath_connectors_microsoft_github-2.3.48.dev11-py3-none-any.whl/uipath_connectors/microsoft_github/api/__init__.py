from .create_branch import (
    create_branch as _create_branch,
    create_branch_async as _create_branch_async,
)
from ..models.create_branch_request import CreateBranchRequest
from ..models.create_branch_response import CreateBranchResponse
from ..models.default_error import DefaultError
from typing import cast
from .create_issues import (
    create_issue as _create_issue,
    create_issue_async as _create_issue_async,
)
from ..models.create_issue_request import CreateIssueRequest
from ..models.create_issue_response import CreateIssueResponse
from .create_pulls import (
    create_pull as _create_pull,
    create_pull_async as _create_pull_async,
)
from ..models.create_pull_request import CreatePullRequest
from ..models.create_pull_response import CreatePullResponse
from .create_repos import (
    create_repo as _create_repo,
    create_repo_async as _create_repo_async,
)
from ..models.create_repo_request import CreateRepoRequest
from ..models.create_repo_response import CreateRepoResponse
from .download_file import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from ..models.download_file_response import DownloadFileResponse
from ..types import File
from io import BytesIO
from .list_branches import (
    list_all_branches as _list_all_branches,
    list_all_branches_async as _list_all_branches_async,
)
from ..models.list_all_branches import ListAllBranches
from .merge_pull_request import (
    merge_pull as _merge_pull,
    merge_pull_async as _merge_pull_async,
)
from ..models.merge_pull_request import MergePullRequest
from ..models.merge_pull_response import MergePullResponse
from .search_issues import (
    search_issues as _search_issues,
    search_issues_async as _search_issues_async,
)
from ..models.search_issues import SearchIssues
from .search_repositories import (
    search_repos as _search_repos,
    search_repos_async as _search_repos_async,
)
from ..models.search_repos import SearchRepos
from .update_issues import (
    update_issue as _update_issue,
    update_issue_async as _update_issue_async,
)
from ..models.update_issue_request import UpdateIssueRequest
from ..models.update_issue_response import UpdateIssueResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class MicrosoftGithub:
    def __init__(self, *, instance_id: str, client: httpx.Client):
        base_url = str(client.base_url).rstrip("/")
        new_headers = {
            k: v for k, v in client.headers.items() if k not in ["content-type"]
        }
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = (
            Client(
                base_url="",  # this will be overridden by the base_url in the Client constructor
            )
            .set_httpx_client(new_client)
            .set_async_httpx_client(new_client_async)
        )

    def create_branch(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        body: CreateBranchRequest,
    ) -> Optional[Union[CreateBranchResponse, DefaultError]]:
        return _create_branch(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            body=body,
        )

    async def create_branch_async(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        body: CreateBranchRequest,
    ) -> Optional[Union[CreateBranchResponse, DefaultError]]:
        return await _create_branch_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            body=body,
        )

    def create_issue(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        body: CreateIssueRequest,
    ) -> Optional[Union[CreateIssueResponse, DefaultError]]:
        return _create_issue(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            body=body,
        )

    async def create_issue_async(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        body: CreateIssueRequest,
    ) -> Optional[Union[CreateIssueResponse, DefaultError]]:
        return await _create_issue_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            body=body,
        )

    def create_pull(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        body: CreatePullRequest,
    ) -> Optional[Union[CreatePullResponse, DefaultError]]:
        return _create_pull(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            body=body,
        )

    async def create_pull_async(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        body: CreatePullRequest,
    ) -> Optional[Union[CreatePullResponse, DefaultError]]:
        return await _create_pull_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            body=body,
        )

    def create_repo(
        self,
        *,
        body: CreateRepoRequest,
    ) -> Optional[Union[CreateRepoResponse, DefaultError]]:
        return _create_repo(
            client=self.client,
            body=body,
        )

    async def create_repo_async(
        self,
        *,
        body: CreateRepoRequest,
    ) -> Optional[Union[CreateRepoResponse, DefaultError]]:
        return await _create_repo_async(
            client=self.client,
            body=body,
        )

    def download_file(
        self,
        *,
        repo: str,
        repo_lookup: Any,
        ref: Optional[str] = None,
        path: str,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_file(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            ref=ref,
            path=path,
        )

    async def download_file_async(
        self,
        *,
        repo: str,
        repo_lookup: Any,
        ref: Optional[str] = None,
        path: str,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_file_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            ref=ref,
            path=path,
        )

    def list_all_branches(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        ref: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["ListAllBranches"]]]:
        return _list_all_branches(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            ref=ref,
        )

    async def list_all_branches_async(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        ref: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["ListAllBranches"]]]:
        return await _list_all_branches_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            ref=ref,
        )

    def merge_pull(
        self,
        repo: str,
        repo_lookup: Any,
        pull_number: str,
        pull_number_lookup: Any,
        *,
        body: MergePullRequest,
    ) -> Optional[Union[DefaultError, MergePullResponse]]:
        return _merge_pull(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            pull_number=pull_number,
            pull_number_lookup=pull_number_lookup,
            body=body,
        )

    async def merge_pull_async(
        self,
        repo: str,
        repo_lookup: Any,
        pull_number: str,
        pull_number_lookup: Any,
        *,
        body: MergePullRequest,
    ) -> Optional[Union[DefaultError, MergePullResponse]]:
        return await _merge_pull_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            pull_number=pull_number,
            pull_number_lookup=pull_number_lookup,
            body=body,
        )

    def search_issues(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        query: str,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchIssues"]]]:
        return _search_issues(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            query=query,
            sort=sort,
            order=order,
        )

    async def search_issues_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        query: str,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchIssues"]]]:
        return await _search_issues_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            query=query,
            sort=sort,
            order=order,
        )

    def search_repos(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        query: str,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchRepos"]]]:
        return _search_repos(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            query=query,
            sort=sort,
            order=order,
        )

    async def search_repos_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        query: str,
        sort: Optional[str] = None,
        order: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["SearchRepos"]]]:
        return await _search_repos_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            query=query,
            sort=sort,
            order=order,
        )

    def update_issue(
        self,
        repo: str,
        repo_lookup: Any,
        issue_number: str,
        issue_number_lookup: Any,
        *,
        body: UpdateIssueRequest,
    ) -> Optional[Union[DefaultError, UpdateIssueResponse]]:
        return _update_issue(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            issue_number=issue_number,
            issue_number_lookup=issue_number_lookup,
            body=body,
        )

    async def update_issue_async(
        self,
        repo: str,
        repo_lookup: Any,
        issue_number: str,
        issue_number_lookup: Any,
        *,
        body: UpdateIssueRequest,
    ) -> Optional[Union[DefaultError, UpdateIssueResponse]]:
        return await _update_issue_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            issue_number=issue_number,
            issue_number_lookup=issue_number_lookup,
            body=body,
        )
