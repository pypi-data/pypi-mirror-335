from .create_issues import (
    create_issue as _create_issue,
    create_issue_async as _create_issue_async,
)
from ..models.create_issue_request import CreateIssueRequest
from ..models.create_issue_response import CreateIssueResponse
from ..models.default_error import DefaultError
from typing import cast
from .create_branch import (
    create_branch as _create_branch,
    create_branch_async as _create_branch_async,
)
from ..models.create_branch_request import CreateBranchRequest
from ..models.create_branch_response import CreateBranchResponse
from .download_file import (
    download_file as _download_file,
    download_file_async as _download_file_async,
)
from ..types import File, FileJsonType
from io import BytesIO
from .update_issues import (
    update_issue as _update_issue,
    update_issue_async as _update_issue_async,
)
from ..models.update_issue_request import UpdateIssueRequest
from ..models.update_issue_response import UpdateIssueResponse
from .create_repos import (
    create_repo as _create_repo,
    create_repo_async as _create_repo_async,
)
from ..models.create_repo_request import CreateRepoRequest
from ..models.create_repo_response import CreateRepoResponse
from .search_repositories import (
    search_repos as _search_repos,
    search_repos_async as _search_repos_async,
)
from ..models.search_repos import SearchRepos
from ..models.search_repos_order import SearchReposOrder
from ..models.search_repos_sort import SearchReposSort
from .merge_pull_request import (
    merge_pull as _merge_pull,
    merge_pull_async as _merge_pull_async,
)
from ..models.merge_pull_request import MergePullRequest
from ..models.merge_pull_response import MergePullResponse
from .list_branches import (
    list_all_branches as _list_all_branches,
    list_all_branches_async as _list_all_branches_async,
)
from ..models.list_all_branches import ListAllBranches
from .search_issues import (
    search_issues as _search_issues,
    search_issues_async as _search_issues_async,
)
from ..models.search_issues import SearchIssues
from .create_pulls import (
    create_pull as _create_pull,
    create_pull_async as _create_pull_async,
)
from ..models.create_pull_request import CreatePullRequest
from ..models.create_pull_response import CreatePullResponse

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

    def download_file(
        self,
        *,
        path: str,
        path_lookup: Any,
        repo: str,
        repo_lookup: Any,
        ref: Optional[str] = None,
        ref_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_file(
            client=self.client,
            path=path,
            path_lookup=path_lookup,
            repo=repo,
            repo_lookup=repo_lookup,
            ref=ref,
            ref_lookup=ref_lookup,
        )

    async def download_file_async(
        self,
        *,
        path: str,
        path_lookup: Any,
        repo: str,
        repo_lookup: Any,
        ref: Optional[str] = None,
        ref_lookup: Any,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_file_async(
            client=self.client,
            path=path,
            path_lookup=path_lookup,
            repo=repo,
            repo_lookup=repo_lookup,
            ref=ref,
            ref_lookup=ref_lookup,
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

    def search_repos(
        self,
        *,
        query: str,
        query_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order: Optional[SearchReposOrder] = None,
        order_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        sort: Optional[SearchReposSort] = None,
        sort_lookup: Any,
    ) -> Optional[Union[DefaultError, list["SearchRepos"]]]:
        return _search_repos(
            client=self.client,
            query=query,
            query_lookup=query_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order=order,
            order_lookup=order_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            sort=sort,
            sort_lookup=sort_lookup,
        )

    async def search_repos_async(
        self,
        *,
        query: str,
        query_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order: Optional[SearchReposOrder] = None,
        order_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        sort: Optional[SearchReposSort] = None,
        sort_lookup: Any,
    ) -> Optional[Union[DefaultError, list["SearchRepos"]]]:
        return await _search_repos_async(
            client=self.client,
            query=query,
            query_lookup=query_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order=order,
            order_lookup=order_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            sort=sort,
            sort_lookup=sort_lookup,
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

    def list_all_branches(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        ref: Optional[str] = None,
        ref_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListAllBranches"]]]:
        return _list_all_branches(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            ref=ref,
            ref_lookup=ref_lookup,
        )

    async def list_all_branches_async(
        self,
        repo: str,
        repo_lookup: Any,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        ref: Optional[str] = None,
        ref_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListAllBranches"]]]:
        return await _list_all_branches_async(
            client=self.client,
            repo=repo,
            repo_lookup=repo_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            ref=ref,
            ref_lookup=ref_lookup,
        )

    def search_issues(
        self,
        *,
        query: str,
        query_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order: Optional[str] = None,
        order_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        sort: Optional[str] = None,
        sort_lookup: Any,
    ) -> Optional[Union[DefaultError, list["SearchIssues"]]]:
        return _search_issues(
            client=self.client,
            query=query,
            query_lookup=query_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order=order,
            order_lookup=order_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            sort=sort,
            sort_lookup=sort_lookup,
        )

    async def search_issues_async(
        self,
        *,
        query: str,
        query_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order: Optional[str] = None,
        order_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        sort: Optional[str] = None,
        sort_lookup: Any,
    ) -> Optional[Union[DefaultError, list["SearchIssues"]]]:
        return await _search_issues_async(
            client=self.client,
            query=query,
            query_lookup=query_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order=order,
            order_lookup=order_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            sort=sort,
            sort_lookup=sort_lookup,
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
