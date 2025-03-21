from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.list_chat_messages import ListChatMessages


def _get_kwargs(
    chat_id: str,
    *,
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["nextPage"] = next_page

    params["where"] = where

    params["orderBy"] = order_by

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/list-normalised-chats/{chat_id}/messages".format(
            chat_id=chat_id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["ListChatMessages"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ListChatMessages.from_dict(response_200_item_data)

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
) -> Response[Union[DefaultError, list["ListChatMessages"]]]:
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
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
) -> Response[Union[DefaultError, list["ListChatMessages"]]]:
    """List All Chat Messages

     Type upto 3 characters of the exact chat group name (case sensitive) or type a custom chat ID, which
    can also be retrieved from the output of 'Get Individual Chat' activity. Dropdown will not retrieve
    results if case sensitivity is not followed

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the case sensitivity of the
            chat group name is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        where (Optional[str]): Add a datetime filter. Must be used along with “Order by” i.e. if
            createdDateTime is selected in “Order by”, filter only on createdDateTime else
            lastModifiedDateTime. Only “gt” and “lt” operators are supported. For example,
            'lastModifiedDateTime gt 2022-09-22T00:00:00.000Z and lastModifiedDateTime lt
            2022-09-24T00:00:00.000Z'
        order_by (Optional[str]): Order the messages based on their respective creation date or
            modified date

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListChatMessages']]]
    """

    if not chat_id and chat_id_lookup:
        filter = chat_id_lookup
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url=f"/chats?where=chatType='group' and topic like '{filter}'"
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
        page_size=page_size,
        next_page=next_page,
        where=where,
        order_by=order_by,
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
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
) -> Optional[Union[DefaultError, list["ListChatMessages"]]]:
    """List All Chat Messages

     Type upto 3 characters of the exact chat group name (case sensitive) or type a custom chat ID, which
    can also be retrieved from the output of 'Get Individual Chat' activity. Dropdown will not retrieve
    results if case sensitivity is not followed

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the case sensitivity of the
            chat group name is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        where (Optional[str]): Add a datetime filter. Must be used along with “Order by” i.e. if
            createdDateTime is selected in “Order by”, filter only on createdDateTime else
            lastModifiedDateTime. Only “gt” and “lt” operators are supported. For example,
            'lastModifiedDateTime gt 2022-09-22T00:00:00.000Z and lastModifiedDateTime lt
            2022-09-24T00:00:00.000Z'
        order_by (Optional[str]): Order the messages based on their respective creation date or
            modified date

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListChatMessages']]
    """

    return sync_detailed(
        chat_id=chat_id,
        chat_id_lookup=chat_id_lookup,
        client=client,
        page_size=page_size,
        next_page=next_page,
        where=where,
        order_by=order_by,
    ).parsed


async def asyncio_detailed(
    chat_id: str,
    chat_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
) -> Response[Union[DefaultError, list["ListChatMessages"]]]:
    """List All Chat Messages

     Type upto 3 characters of the exact chat group name (case sensitive) or type a custom chat ID, which
    can also be retrieved from the output of 'Get Individual Chat' activity. Dropdown will not retrieve
    results if case sensitivity is not followed

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the case sensitivity of the
            chat group name is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        where (Optional[str]): Add a datetime filter. Must be used along with “Order by” i.e. if
            createdDateTime is selected in “Order by”, filter only on createdDateTime else
            lastModifiedDateTime. Only “gt” and “lt” operators are supported. For example,
            'lastModifiedDateTime gt 2022-09-22T00:00:00.000Z and lastModifiedDateTime lt
            2022-09-24T00:00:00.000Z'
        order_by (Optional[str]): Order the messages based on their respective creation date or
            modified date

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['ListChatMessages']]]
    """

    if not chat_id and chat_id_lookup:
        filter = chat_id_lookup
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url=f"/chats?where=chatType='group' and topic like '{filter}'"
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
        page_size=page_size,
        next_page=next_page,
        where=where,
        order_by=order_by,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    chat_id: str,
    chat_id_lookup: Any,
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    where: Optional[str] = None,
    order_by: Optional[str] = None,
) -> Optional[Union[DefaultError, list["ListChatMessages"]]]:
    """List All Chat Messages

     Type upto 3 characters of the exact chat group name (case sensitive) or type a custom chat ID, which
    can also be retrieved from the output of 'Get Individual Chat' activity. Dropdown will not retrieve
    results if case sensitivity is not followed

    Args:
        chat_id (str): Type upto 3 characters of the exact chat group name (case sensitive) or
            type a custom chat ID. Dropdown will not retrieve results if the case sensitivity of the
            chat group name is not followed
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        where (Optional[str]): Add a datetime filter. Must be used along with “Order by” i.e. if
            createdDateTime is selected in “Order by”, filter only on createdDateTime else
            lastModifiedDateTime. Only “gt” and “lt” operators are supported. For example,
            'lastModifiedDateTime gt 2022-09-22T00:00:00.000Z and lastModifiedDateTime lt
            2022-09-24T00:00:00.000Z'
        order_by (Optional[str]): Order the messages based on their respective creation date or
            modified date

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['ListChatMessages']]
    """

    return (
        await asyncio_detailed(
            chat_id=chat_id,
            chat_id_lookup=chat_id_lookup,
            client=client,
            page_size=page_size,
            next_page=next_page,
            where=where,
            order_by=order_by,
        )
    ).parsed
