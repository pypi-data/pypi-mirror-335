from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_team_by_name_response import GetTeamByNameResponse


def _get_kwargs(
    *,
    name: str,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["Name"] = name

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/team-by-name",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetTeamByNameResponse]]:
    if response.status_code == 200:
        response_200 = GetTeamByNameResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetTeamByNameResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
    name_lookup: Any,
) -> Response[Union[DefaultError, GetTeamByNameResponse]]:
    """Get Team by Name

     Retrieve the team in your current organization based on a team name

    Args:
        name (str): Type a custom name or select from the dropdown

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetTeamByNameResponse]]
    """

    if not name and name_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/teams"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if name_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for name_lookup in teams")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for name_lookup in teams. Using the first match."
            )

        name = found_items[0]["displayName"]

    kwargs = _get_kwargs(
        name=name,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
    name_lookup: Any,
) -> Optional[Union[DefaultError, GetTeamByNameResponse]]:
    """Get Team by Name

     Retrieve the team in your current organization based on a team name

    Args:
        name (str): Type a custom name or select from the dropdown

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetTeamByNameResponse]
    """

    return sync_detailed(
        client=client,
        name=name,
        name_lookup=name_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
    name_lookup: Any,
) -> Response[Union[DefaultError, GetTeamByNameResponse]]:
    """Get Team by Name

     Retrieve the team in your current organization based on a team name

    Args:
        name (str): Type a custom name or select from the dropdown

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetTeamByNameResponse]]
    """

    if not name and name_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/teams"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if name_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for name_lookup in teams")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for name_lookup in teams. Using the first match."
            )

        name = found_items[0]["displayName"]

    kwargs = _get_kwargs(
        name=name,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    name: str,
    name_lookup: Any,
) -> Optional[Union[DefaultError, GetTeamByNameResponse]]:
    """Get Team by Name

     Retrieve the team in your current organization based on a team name

    Args:
        name (str): Type a custom name or select from the dropdown

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetTeamByNameResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            name=name,
            name_lookup=name_lookup,
        )
    ).parsed
