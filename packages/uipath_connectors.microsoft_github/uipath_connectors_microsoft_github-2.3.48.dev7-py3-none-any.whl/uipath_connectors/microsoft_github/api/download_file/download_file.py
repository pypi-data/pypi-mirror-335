from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...types import File
from io import BytesIO


def _get_kwargs(
    *,
    path: str,
    repo: str,
    ref: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["path"] = path

    params["repo"] = repo

    params["ref"] = ref

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/download_file",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, File]]:
    if response.status_code == 200:
        response_200 = File(payload=BytesIO(response.content))

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
) -> Response[Union[DefaultError, File]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    path: str,
    path_lookup: Any,
    repo: str,
    repo_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Response[Union[DefaultError, File]]:
    """Download File

     Downloads a file from Github

    Args:
        path (str):
        repo (str):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, File]]
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
        path=path,
        repo=repo,
        ref=ref,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    path: str,
    path_lookup: Any,
    repo: str,
    repo_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Optional[Union[DefaultError, File]]:
    """Download File

     Downloads a file from Github

    Args:
        path (str):
        repo (str):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, File]
    """

    return sync_detailed(
        client=client,
        path=path,
        path_lookup=path_lookup,
        repo=repo,
        repo_lookup=repo_lookup,
        ref=ref,
        ref_lookup=ref_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    path: str,
    path_lookup: Any,
    repo: str,
    repo_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Response[Union[DefaultError, File]]:
    """Download File

     Downloads a file from Github

    Args:
        path (str):
        repo (str):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, File]]
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
        path=path,
        repo=repo,
        ref=ref,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    path: str,
    path_lookup: Any,
    repo: str,
    repo_lookup: Any,
    ref: Optional[str] = None,
    ref_lookup: Any,
) -> Optional[Union[DefaultError, File]]:
    """Download File

     Downloads a file from Github

    Args:
        path (str):
        repo (str):
        ref (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, File]
    """

    return (
        await asyncio_detailed(
            client=client,
            path=path,
            path_lookup=path_lookup,
            repo=repo,
            repo_lookup=repo_lookup,
            ref=ref,
            ref_lookup=ref_lookup,
        )
    ).parsed
