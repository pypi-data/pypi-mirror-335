from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.list_all_branches import ListAllBranches


def _get_kwargs(
    repo: str,
    *,
    fields: Optional[str] = None,
    next_page: Optional[str] = None,
    page_size: Optional[int] = None,
    ref: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["fields"] = fields

    params["nextPage"] = next_page

    params["pageSize"] = page_size

    params["ref"] = ref

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/{repo}/list_branches".format(
            repo=repo,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["ListAllBranches"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_list_all_branches_list_item_data in _response_200:
            componentsschemas_list_all_branches_list_item = ListAllBranches.from_dict(
                componentsschemas_list_all_branches_list_item_data
            )

            response_200.append(componentsschemas_list_all_branches_list_item)

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
) -> Response[Union[DefaultError, list["ListAllBranches"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    repo: str,
    repo_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Response[Union[DefaultError, list["ListAllBranches"]]]:
    """List All Branches

     Lists all the branches for a repository in Github

    Args:
        repo (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListAllBranches']]]
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

    kwargs = _get_kwargs(
        repo=repo,
        fields=fields,
        next_page=next_page,
        page_size=page_size,
        ref=ref,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    repo: str,
    repo_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Optional[Union[DefaultError, list["ListAllBranches"]]]:
    """List All Branches

     Lists all the branches for a repository in Github

    Args:
        repo (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListAllBranches']]
    """

    return sync_detailed(
        repo=repo,
        repo_lookup=repo_lookup,
        client=client,
        fields=fields,
        fields_lookup=fields_lookup,
        next_page=next_page,
        next_page_lookup=next_page_lookup,
        page_size=page_size,
        page_size_lookup=page_size_lookup,
        ref=ref,
        ref_lookup=ref_lookup,
    ).parsed


async def asyncio_detailed(
    repo: str,
    repo_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Response[Union[DefaultError, list["ListAllBranches"]]]:
    """List All Branches

     Lists all the branches for a repository in Github

    Args:
        repo (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListAllBranches']]]
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

    kwargs = _get_kwargs(
        repo=repo,
        fields=fields,
        next_page=next_page,
        page_size=page_size,
        ref=ref,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    repo: str,
    repo_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Optional[Union[DefaultError, list["ListAllBranches"]]]:
    """List All Branches

     Lists all the branches for a repository in Github

    Args:
        repo (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        page_size (Optional[int]):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListAllBranches']]
    """

    return (
        await asyncio_detailed(
            repo=repo,
            repo_lookup=repo_lookup,
            client=client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            ref=ref,
            ref_lookup=ref_lookup,
        )
    ).parsed
