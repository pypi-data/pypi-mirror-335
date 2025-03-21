from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.getonline_meetings_response import GetonlineMeetingsResponse


def _get_kwargs(
    *,
    get_by: str,
    join_meeting_id: Optional[str] = None,
    join_meeting_url: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["getBy"] = get_by

    params["joinMeetingID"] = join_meeting_id

    params["joinMeetingURL"] = join_meeting_url

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/curated_online_meetings",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetonlineMeetingsResponse]]:
    if response.status_code == 200:
        response_200 = GetonlineMeetingsResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetonlineMeetingsResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    get_by: str,
    join_meeting_id: Optional[str] = None,
    join_meeting_url: Optional[str] = None,
) -> Response[Union[DefaultError, GetonlineMeetingsResponse]]:
    """Get Online Teams Meeting

     Retrieve an online meeting using join meeting ID or join meeting URL

    Args:
        get_by (str): Retrieve meeting by join meeting ID or join meeting URL. Both can be found
            in the Outlook / Teams calendar invite
        join_meeting_id (Optional[str]): Provide join meeting ID to retrieve online meeting
        join_meeting_url (Optional[str]): Provide join meeting URL to retreive online meeting

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetonlineMeetingsResponse]]
    """

    kwargs = _get_kwargs(
        get_by=get_by,
        join_meeting_id=join_meeting_id,
        join_meeting_url=join_meeting_url,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    get_by: str,
    join_meeting_id: Optional[str] = None,
    join_meeting_url: Optional[str] = None,
) -> Optional[Union[DefaultError, GetonlineMeetingsResponse]]:
    """Get Online Teams Meeting

     Retrieve an online meeting using join meeting ID or join meeting URL

    Args:
        get_by (str): Retrieve meeting by join meeting ID or join meeting URL. Both can be found
            in the Outlook / Teams calendar invite
        join_meeting_id (Optional[str]): Provide join meeting ID to retrieve online meeting
        join_meeting_url (Optional[str]): Provide join meeting URL to retreive online meeting

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetonlineMeetingsResponse]
    """

    return sync_detailed(
        client=client,
        get_by=get_by,
        join_meeting_id=join_meeting_id,
        join_meeting_url=join_meeting_url,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    get_by: str,
    join_meeting_id: Optional[str] = None,
    join_meeting_url: Optional[str] = None,
) -> Response[Union[DefaultError, GetonlineMeetingsResponse]]:
    """Get Online Teams Meeting

     Retrieve an online meeting using join meeting ID or join meeting URL

    Args:
        get_by (str): Retrieve meeting by join meeting ID or join meeting URL. Both can be found
            in the Outlook / Teams calendar invite
        join_meeting_id (Optional[str]): Provide join meeting ID to retrieve online meeting
        join_meeting_url (Optional[str]): Provide join meeting URL to retreive online meeting

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetonlineMeetingsResponse]]
    """

    kwargs = _get_kwargs(
        get_by=get_by,
        join_meeting_id=join_meeting_id,
        join_meeting_url=join_meeting_url,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    get_by: str,
    join_meeting_id: Optional[str] = None,
    join_meeting_url: Optional[str] = None,
) -> Optional[Union[DefaultError, GetonlineMeetingsResponse]]:
    """Get Online Teams Meeting

     Retrieve an online meeting using join meeting ID or join meeting URL

    Args:
        get_by (str): Retrieve meeting by join meeting ID or join meeting URL. Both can be found
            in the Outlook / Teams calendar invite
        join_meeting_id (Optional[str]): Provide join meeting ID to retrieve online meeting
        join_meeting_url (Optional[str]): Provide join meeting URL to retreive online meeting

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetonlineMeetingsResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            get_by=get_by,
            join_meeting_id=join_meeting_id,
            join_meeting_url=join_meeting_url,
        )
    ).parsed
