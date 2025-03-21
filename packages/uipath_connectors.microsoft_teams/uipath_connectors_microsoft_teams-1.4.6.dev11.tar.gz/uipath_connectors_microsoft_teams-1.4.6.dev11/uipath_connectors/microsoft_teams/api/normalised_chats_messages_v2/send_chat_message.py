from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.send_chat_message_body import SendChatMessageBody
from ...models.send_chat_message_response import SendChatMessageResponse


def _get_kwargs(
    chat_id: str,
    *,
    body: SendChatMessageBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/normalised-chats/{chat_id}/messages-v2/drive/items".format(
            chat_id=chat_id,
        ),
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, SendChatMessageResponse]]:
    if response.status_code == 200:
        response_200 = SendChatMessageResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, SendChatMessageResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    chat_id: str,
    chat_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SendChatMessageBody,
) -> Response[Union[DefaultError, SendChatMessageResponse]]:
    """Send Group Chat Message

     Send a message in an existing group chat with an option to attach SharePoint files

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the chat group name case
            sensitivity is not followed
        body (SendChatMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, SendChatMessageResponse]]
    """

    if not chat_id and chat_id_lookup:
        filter = chat_id_lookup
        lookup_response_raw = client.get_httpx_client().request(
            method="get",
            url=f"/chats?$filter=chatType eq 'group' and contains(tolower(topic),tolower('{filter}'))",
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError("No matches found for chat_id_lookup in chats")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for chat_id_lookup in chats. Using the first match."
            )

        chat_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        chat_id=chat_id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    chat_id: str,
    chat_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SendChatMessageBody,
) -> Optional[Union[DefaultError, SendChatMessageResponse]]:
    """Send Group Chat Message

     Send a message in an existing group chat with an option to attach SharePoint files

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the chat group name case
            sensitivity is not followed
        body (SendChatMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, SendChatMessageResponse]
    """

    return sync_detailed(
        chat_id=chat_id,
        chat_id_lookup=chat_id_lookup,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    chat_id: str,
    chat_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SendChatMessageBody,
) -> Response[Union[DefaultError, SendChatMessageResponse]]:
    """Send Group Chat Message

     Send a message in an existing group chat with an option to attach SharePoint files

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the chat group name case
            sensitivity is not followed
        body (SendChatMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, SendChatMessageResponse]]
    """

    if not chat_id and chat_id_lookup:
        filter = chat_id_lookup
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get",
            url=f"/chats?$filter=chatType eq 'group' and contains(tolower(topic),tolower('{filter}'))",
        )
        lookup_response = lookup_response_raw.json()

        found_items = lookup_response

        if not found_items:
            raise ValueError("No matches found for chat_id_lookup in chats")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for chat_id_lookup in chats. Using the first match."
            )

        chat_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        chat_id=chat_id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chat_id: str,
    chat_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    body: SendChatMessageBody,
) -> Optional[Union[DefaultError, SendChatMessageResponse]]:
    """Send Group Chat Message

     Send a message in an existing group chat with an option to attach SharePoint files

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the chat group name case
            sensitivity is not followed
        body (SendChatMessageBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, SendChatMessageResponse]
    """

    return (
        await asyncio_detailed(
            chat_id=chat_id,
            chat_id_lookup=chat_id_lookup,
            client=client,
            body=body,
        )
    ).parsed
