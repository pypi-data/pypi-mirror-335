from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.search_issueby_jql import SearchIssuebyJQL


def _get_kwargs(
    *,
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    jql: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["nextPage"] = next_page

    params["jql"] = jql

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["SearchIssuebyJQL"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_data in _response_200:
            response_200 = SearchIssuebyJQL.from_dict(response_200_data)

            response_200.append(response_200)

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
) -> Response[Union[DefaultError, list["SearchIssuebyJQL"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    jql: Optional[str] = None,
) -> Response[Union[DefaultError, list["SearchIssuebyJQL"]]]:
    """Search Issues by JQL

     Allows for advanced search using Jira Query Language (JQL)

    Args:
        page_size (Optional[int]): The maximum number of items to return per page. To manage page
            size, Jira may return fewer items per page where a large number of fields are requested.
            The greatest number of items returned per page is achieved when requesting `id` or `key`
            only.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        jql (Optional[str]): The string containing the JQL used to filter out issues

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchIssuebyJQL']]]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        jql=jql,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    jql: Optional[str] = None,
) -> Optional[Union[DefaultError, list["SearchIssuebyJQL"]]]:
    """Search Issues by JQL

     Allows for advanced search using Jira Query Language (JQL)

    Args:
        page_size (Optional[int]): The maximum number of items to return per page. To manage page
            size, Jira may return fewer items per page where a large number of fields are requested.
            The greatest number of items returned per page is achieved when requesting `id` or `key`
            only.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        jql (Optional[str]): The string containing the JQL used to filter out issues

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchIssuebyJQL']]
    """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_page=next_page,
        jql=jql,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    jql: Optional[str] = None,
) -> Response[Union[DefaultError, list["SearchIssuebyJQL"]]]:
    """Search Issues by JQL

     Allows for advanced search using Jira Query Language (JQL)

    Args:
        page_size (Optional[int]): The maximum number of items to return per page. To manage page
            size, Jira may return fewer items per page where a large number of fields are requested.
            The greatest number of items returned per page is achieved when requesting `id` or `key`
            only.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        jql (Optional[str]): The string containing the JQL used to filter out issues

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['SearchIssuebyJQL']]]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        jql=jql,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    jql: Optional[str] = None,
) -> Optional[Union[DefaultError, list["SearchIssuebyJQL"]]]:
    """Search Issues by JQL

     Allows for advanced search using Jira Query Language (JQL)

    Args:
        page_size (Optional[int]): The maximum number of items to return per page. To manage page
            size, Jira may return fewer items per page where a large number of fields are requested.
            The greatest number of items returned per page is achieved when requesting `id` or `key`
            only.
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        jql (Optional[str]): The string containing the JQL used to filter out issues

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['SearchIssuebyJQL']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_page=next_page,
            jql=jql,
        )
    ).parsed
