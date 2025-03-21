from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.list_channel_messages import ListChannelMessages


def _get_kwargs(
    team_id: str,
    channel_id: str,
    *,
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    expand: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["nextPage"] = next_page

    params["expand"] = expand

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/list-normalised-teams/{team_id}/channels/{channel_id}/messages".format(
            team_id=team_id,
            channel_id=channel_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["ListChannelMessages"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListChannelMessages.from_dict(response_200_item_data)

            response_200.append(response_200_item)

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
) -> Response[Union[DefaultError, list["ListChannelMessages"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    team_id: str,
    team_id_lookup: Any,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    expand: Optional[str] = None,
) -> Response[Union[DefaultError, list["ListChannelMessages"]]]:
    """List All Channel Messages

     Retrieves the list of messages in a channel

    Args:
        team_id (str): Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        expand (Optional[str]): To get the properties of channel messages that are replies. By
            default, a response can include up to 1000 replies

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListChannelMessages']]]
    """

    if not team_id and team_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/teams"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if team_id_lookup in item["id"] or team_id_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for team_id_lookup in teams")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for team_id_lookup in teams. Using the first match."
            )

        team_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        team_id=team_id,
        channel_id=channel_id,
        page_size=page_size,
        next_page=next_page,
        expand=expand,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    team_id: str,
    team_id_lookup: Any,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    expand: Optional[str] = None,
) -> Optional[Union[DefaultError, list["ListChannelMessages"]]]:
    """List All Channel Messages

     Retrieves the list of messages in a channel

    Args:
        team_id (str): Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        expand (Optional[str]): To get the properties of channel messages that are replies. By
            default, a response can include up to 1000 replies

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListChannelMessages']]
    """

    return sync_detailed(
        team_id=team_id,
        team_id_lookup=team_id_lookup,
        channel_id=channel_id,
        client=client,
        page_size=page_size,
        next_page=next_page,
        expand=expand,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    team_id_lookup: Any,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    expand: Optional[str] = None,
) -> Response[Union[DefaultError, list["ListChannelMessages"]]]:
    """List All Channel Messages

     Retrieves the list of messages in a channel

    Args:
        team_id (str): Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        expand (Optional[str]): To get the properties of channel messages that are replies. By
            default, a response can include up to 1000 replies

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListChannelMessages']]]
    """

    if not team_id and team_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/teams"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if team_id_lookup in item["id"] or team_id_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for team_id_lookup in teams")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for team_id_lookup in teams. Using the first match."
            )

        team_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        team_id=team_id,
        channel_id=channel_id,
        page_size=page_size,
        next_page=next_page,
        expand=expand,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    team_id_lookup: Any,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    expand: Optional[str] = None,
) -> Optional[Union[DefaultError, list["ListChannelMessages"]]]:
    """List All Channel Messages

     Retrieves the list of messages in a channel

    Args:
        team_id (str): Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        expand (Optional[str]): To get the properties of channel messages that are replies. By
            default, a response can include up to 1000 replies

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListChannelMessages']]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            team_id_lookup=team_id_lookup,
            channel_id=channel_id,
            client=client,
            page_size=page_size,
            next_page=next_page,
            expand=expand,
        )
    ).parsed
