from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.send_channel_message_body import SendChannelMessageBody
from ...models.send_channel_message_response import SendChannelMessageResponse


def _get_kwargs(
    team_id: str,
    channel_id: str,
    *,
    body: SendChannelMessageBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/normalised-teams/{team_id}/channels/{channel_id}/messages-v2/drive/items".format(
            team_id=team_id,
            channel_id=channel_id,
        ),
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, SendChannelMessageResponse]]:
    if response.status_code == 200:
        response_200 = SendChannelMessageResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, SendChannelMessageResponse]]:
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
    body: SendChannelMessageBody,
) -> Response[Union[DefaultError, SendChannelMessageResponse]]:
    """Send Channel Message

     Send a message in a team channel with an option to attach SharePoint files

    Args:
        team_id (str):  Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        body (SendChannelMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, SendChannelMessageResponse]]
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
        body=body,
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
    body: SendChannelMessageBody,
) -> Optional[Union[DefaultError, SendChannelMessageResponse]]:
    """Send Channel Message

     Send a message in a team channel with an option to attach SharePoint files

    Args:
        team_id (str):  Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        body (SendChannelMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, SendChannelMessageResponse]
    """

    return sync_detailed(
        team_id=team_id,
        team_id_lookup=team_id_lookup,
        channel_id=channel_id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    team_id: str,
    team_id_lookup: Any,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SendChannelMessageBody,
) -> Response[Union[DefaultError, SendChannelMessageResponse]]:
    """Send Channel Message

     Send a message in a team channel with an option to attach SharePoint files

    Args:
        team_id (str):  Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        body (SendChannelMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, SendChannelMessageResponse]]
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
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    team_id: str,
    team_id_lookup: Any,
    channel_id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SendChannelMessageBody,
) -> Optional[Union[DefaultError, SendChannelMessageResponse]]:
    """Send Channel Message

     Send a message in a team channel with an option to attach SharePoint files

    Args:
        team_id (str):  Type the name to retrieve the team from the dropdown or type a custom team
            ID. You can also retrieve the team ID from the output parameter of “Get Team by Name”
            activity
        channel_id (str): Type upto 3 characters of the exact channel name (case sensitive) or
            type a custom channel ID. The ID of the channel can also be retrieved from the output
            parameter “ID” of the “Get Channel by Name” activity. Dropdown will not retrieve results
            if the channel name case sensitivity is not followed
        body (SendChannelMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, SendChannelMessageResponse]
    """

    return (
        await asyncio_detailed(
            team_id=team_id,
            team_id_lookup=team_id_lookup,
            channel_id=channel_id,
            client=client,
            body=body,
        )
    ).parsed
