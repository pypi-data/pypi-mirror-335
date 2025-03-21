from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_issue_response import GetIssueResponse


def _get_kwargs(
    issue_id: str,
    *,
    project: str,
    issuetype: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["project"] = project

    params["issuetype"] = issuetype

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/curated_get_issue/{issue_id}".format(
            issue_id=issue_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetIssueResponse]]:
    if response.status_code == 200:
        response_200 = GetIssueResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetIssueResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    issue_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    project: str,
    project_lookup: Any,
    issuetype: str,
) -> Response[Union[DefaultError, GetIssueResponse]]:
    """Get Issue

     Returns all the information of a Jira issue (assignee, reporter, project, etc)

    Args:
        issue_id (str): The issue key (ABCD-1234) or issue ID
        project (str): The unique key of the project
        issuetype (str): The type of the issue (task, story, bug, epic, etc). Select one to enable
            custom fields

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetIssueResponse]]
    """

    if not project and project_lookup:
        filter = project_lookup
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url=f"/project/search?query={filter}"
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError("No matches found for project_lookup in project")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for project_lookup in project. Using the first match."
            )

        project = found_items[0]["key"]

    kwargs = _get_kwargs(
        issue_id=issue_id,
        project=project,
        issuetype=issuetype,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    issue_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    project: str,
    project_lookup: Any,
    issuetype: str,
) -> Optional[Union[DefaultError, GetIssueResponse]]:
    """Get Issue

     Returns all the information of a Jira issue (assignee, reporter, project, etc)

    Args:
        issue_id (str): The issue key (ABCD-1234) or issue ID
        project (str): The unique key of the project
        issuetype (str): The type of the issue (task, story, bug, epic, etc). Select one to enable
            custom fields

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetIssueResponse]
    """

    return sync_detailed(
        issue_id=issue_id,
        client=client,
        project=project,
        project_lookup=project_lookup,
        issuetype=issuetype,
    ).parsed


async def asyncio_detailed(
    issue_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    project: str,
    project_lookup: Any,
    issuetype: str,
) -> Response[Union[DefaultError, GetIssueResponse]]:
    """Get Issue

     Returns all the information of a Jira issue (assignee, reporter, project, etc)

    Args:
        issue_id (str): The issue key (ABCD-1234) or issue ID
        project (str): The unique key of the project
        issuetype (str): The type of the issue (task, story, bug, epic, etc). Select one to enable
            custom fields

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetIssueResponse]]
    """

    if not project and project_lookup:
        filter = project_lookup
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url=f"/project/search?query={filter}"
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError("No matches found for project_lookup in project")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for project_lookup in project. Using the first match."
            )

        project = found_items[0]["key"]

    kwargs = _get_kwargs(
        issue_id=issue_id,
        project=project,
        issuetype=issuetype,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    issue_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    project: str,
    project_lookup: Any,
    issuetype: str,
) -> Optional[Union[DefaultError, GetIssueResponse]]:
    """Get Issue

     Returns all the information of a Jira issue (assignee, reporter, project, etc)

    Args:
        issue_id (str): The issue key (ABCD-1234) or issue ID
        project (str): The unique key of the project
        issuetype (str): The type of the issue (task, story, bug, epic, etc). Select one to enable
            custom fields

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetIssueResponse]
    """

    return (
        await asyncio_detailed(
            issue_id=issue_id,
            client=client,
            project=project,
            project_lookup=project_lookup,
            issuetype=issuetype,
        )
    ).parsed
