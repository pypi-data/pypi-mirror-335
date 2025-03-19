from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.search_repos import SearchRepos
from ...models.search_repos_order import SearchReposOrder
from ...models.search_repos_sort import SearchReposSort


def _get_kwargs(
    *,
    query: str,
    fields: Optional[str] = None,
    next_page: Optional[str] = None,
    order: Optional[SearchReposOrder] = None,
    page_size: Optional[int] = None,
    sort: Optional[SearchReposSort] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["query"] = query

    params["fields"] = fields

    params["nextPage"] = next_page

    json_order: Optional[str] = None
    if order is not None:
        json_order = order.value

    params["order"] = json_order

    params["pageSize"] = page_size

    json_sort: Optional[str] = None
    if sort is not None:
        json_sort = sort.value

    params["sort"] = json_sort

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search_repositories",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["SearchRepos"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_search_repos_list_item_data in _response_200:
            componentsschemas_search_repos_list_item = SearchRepos.from_dict(
                componentsschemas_search_repos_list_item_data
            )

            response_200.append(componentsschemas_search_repos_list_item)

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
) -> Response[Union[DefaultError, list["SearchRepos"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
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
) -> Response[Union[DefaultError, list["SearchRepos"]]]:
    """Search Repositories

     Searches for a repository in Github

    Args:
        query (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        order (Optional[SearchReposOrder]):
        page_size (Optional[int]):
        sort (Optional[SearchReposSort]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchRepos']]]
    """

    kwargs = _get_kwargs(
        query=query,
        fields=fields,
        next_page=next_page,
        order=order,
        page_size=page_size,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
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
    """Search Repositories

     Searches for a repository in Github

    Args:
        query (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        order (Optional[SearchReposOrder]):
        page_size (Optional[int]):
        sort (Optional[SearchReposSort]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchRepos']]
    """

    return sync_detailed(
        client=client,
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
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
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
) -> Response[Union[DefaultError, list["SearchRepos"]]]:
    """Search Repositories

     Searches for a repository in Github

    Args:
        query (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        order (Optional[SearchReposOrder]):
        page_size (Optional[int]):
        sort (Optional[SearchReposSort]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchRepos']]]
    """

    kwargs = _get_kwargs(
        query=query,
        fields=fields,
        next_page=next_page,
        order=order,
        page_size=page_size,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
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
    """Search Repositories

     Searches for a repository in Github

    Args:
        query (str):
        fields (Optional[str]):
        next_page (Optional[str]):
        order (Optional[SearchReposOrder]):
        page_size (Optional[int]):
        sort (Optional[SearchReposSort]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchRepos']]
    """

    return (
        await asyncio_detailed(
            client=client,
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
    ).parsed
