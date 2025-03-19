from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.merge_pull_request import MergePullRequest
from ...models.merge_pull_response import MergePullResponse


def _get_kwargs(
    repo: str,
    pull_number: str,
    *,
    body: MergePullRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/{repo}/pulls/{pull_number}/merge".format(
            repo=repo,
            pull_number=pull_number,
        ),
    }

    _body = body.to_dict()

    _kwargs["json"] = _body
    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, MergePullResponse]]:
    if response.status_code == 200:
        response_200 = MergePullResponse.from_dict(response.json())

        return response_200
    if response.status_code == 400:
        response_400 = DefaultError.from_dict(response.json())

        return response_400
    if response.status_code == 401:
        response_401 = DefaultError.from_dict(response.json())

        return response_401
    if response.status_code == 403:
        response_403 = DefaultError.from_dict(response.json())

        return response_403
    if response.status_code == 404:
        response_404 = DefaultError.from_dict(response.json())

        return response_404
    if response.status_code == 405:
        response_405 = DefaultError.from_dict(response.json())

        return response_405
    if response.status_code == 406:
        response_406 = DefaultError.from_dict(response.json())

        return response_406
    if response.status_code == 409:
        response_409 = DefaultError.from_dict(response.json())

        return response_409
    if response.status_code == 415:
        response_415 = DefaultError.from_dict(response.json())

        return response_415
    if response.status_code == 500:
        response_500 = DefaultError.from_dict(response.json())

        return response_500
    if response.status_code == 402:
        response_402 = DefaultError.from_dict(response.json())

        return response_402
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[DefaultError, MergePullResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repo: str,
    repo_lookup: Any,
    pull_number: str,
    pull_number_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: MergePullRequest,
) -> Response[Union[DefaultError, MergePullResponse]]:
    """Merge Pull Request

     Merges a pull request in Github

    Args:
        repo (str):
        pull_number (str):
        body (MergePullRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, MergePullResponse]]
    """

    if not repo and repo_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/repos"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if repo_lookup in item["name"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for repo_lookup in repos")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for repo_lookup in repos. Using the first match."
            )

        repo = found_items[0]["name"]
    if not pull_number and pull_number_lookup:
        filter = pull_number_lookup
        lookup_response_raw = client.get_httpx_client().request(
            method="get",
            url=f"/search_issues?sort=updated?query=type:pulls org:orgName %22{filter}%22in:title",
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError(
                "No matches found for pull_number_lookup in search_issues?sort=updated"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for pull_number_lookup in search_issues?sort=updated. Using the first match."
            )

        pull_number = found_items[0]["number"]

    kwargs = _get_kwargs(
        repo=repo,
        pull_number=pull_number,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repo: str,
    repo_lookup: Any,
    pull_number: str,
    pull_number_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: MergePullRequest,
) -> Optional[Union[DefaultError, MergePullResponse]]:
    """Merge Pull Request

     Merges a pull request in Github

    Args:
        repo (str):
        pull_number (str):
        body (MergePullRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, MergePullResponse]
    """

    return sync_detailed(
        repo=repo,
        repo_lookup=repo_lookup,
        pull_number=pull_number,
        pull_number_lookup=pull_number_lookup,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    repo: str,
    repo_lookup: Any,
    pull_number: str,
    pull_number_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: MergePullRequest,
) -> Response[Union[DefaultError, MergePullResponse]]:
    """Merge Pull Request

     Merges a pull request in Github

    Args:
        repo (str):
        pull_number (str):
        body (MergePullRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, MergePullResponse]]
    """

    if not repo and repo_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/repos"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if repo_lookup in item["name"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for repo_lookup in repos")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for repo_lookup in repos. Using the first match."
            )

        repo = found_items[0]["name"]
    if not pull_number and pull_number_lookup:
        filter = pull_number_lookup
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get",
            url=f"/search_issues?sort=updated?query=type:pulls org:orgName %22{filter}%22in:title",
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError(
                "No matches found for pull_number_lookup in search_issues?sort=updated"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for pull_number_lookup in search_issues?sort=updated. Using the first match."
            )

        pull_number = found_items[0]["number"]

    kwargs = _get_kwargs(
        repo=repo,
        pull_number=pull_number,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repo: str,
    repo_lookup: Any,
    pull_number: str,
    pull_number_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: MergePullRequest,
) -> Optional[Union[DefaultError, MergePullResponse]]:
    """Merge Pull Request

     Merges a pull request in Github

    Args:
        repo (str):
        pull_number (str):
        body (MergePullRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, MergePullResponse]
    """

    return (
        await asyncio_detailed(
            repo=repo,
            repo_lookup=repo_lookup,
            pull_number=pull_number,
            pull_number_lookup=pull_number_lookup,
            client=client,
            body=body,
        )
    ).parsed
