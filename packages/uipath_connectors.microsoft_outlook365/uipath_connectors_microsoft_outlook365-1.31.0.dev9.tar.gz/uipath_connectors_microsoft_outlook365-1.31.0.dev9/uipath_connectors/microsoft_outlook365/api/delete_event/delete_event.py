from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError


def _get_kwargs(
    id: str,
    *,
    comment: Optional[str] = None,
    calendar_id: Optional[str] = None,
    delete_option: Optional[str] = "singleInstance",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["comment"] = comment

    params["calendarID"] = calendar_id

    params["deleteOption"] = delete_option

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/DeleteEvent/{id}".format(
            id=id,
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[Any, DefaultError]]:
    if response.status_code == 200:
        response_200 = cast(Any, None)
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
) -> Response[Union[Any, DefaultError]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    comment: Optional[str] = None,
    calendar_id: Optional[str] = None,
    calendar_id_lookup: Any,
    delete_option: Optional[str] = "singleInstance",
) -> Response[Union[Any, DefaultError]]:
    """Delete Event (Calendar Event)

    Args:
        id (str): The ID of event to cancel/delete
        comment (Optional[str]): The message sent to the attendees/organizer of the deleted event
        calendar_id (Optional[str]): The ID of calendar in which respective event is present.
            Should be left empty for personal calendar.
        delete_option (Optional[str]): Indicates option for event deletion Default:
            'singleInstance'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
    """

    if not calendar_id and calendar_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/CalendarList"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if calendar_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for calendar_id_lookup in CalendarList")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for calendar_id_lookup in CalendarList. Using the first match."
            )

        calendar_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        id=id,
        comment=comment,
        calendar_id=calendar_id,
        delete_option=delete_option,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    comment: Optional[str] = None,
    calendar_id: Optional[str] = None,
    calendar_id_lookup: Any,
    delete_option: Optional[str] = "singleInstance",
) -> Optional[Union[Any, DefaultError]]:
    """Delete Event (Calendar Event)

    Args:
        id (str): The ID of event to cancel/delete
        comment (Optional[str]): The message sent to the attendees/organizer of the deleted event
        calendar_id (Optional[str]): The ID of calendar in which respective event is present.
            Should be left empty for personal calendar.
        delete_option (Optional[str]): Indicates option for event deletion Default:
            'singleInstance'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return sync_detailed(
        id=id,
        client=client,
        comment=comment,
        calendar_id=calendar_id,
        calendar_id_lookup=calendar_id_lookup,
        delete_option=delete_option,
    ).parsed


async def asyncio_detailed(
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    comment: Optional[str] = None,
    calendar_id: Optional[str] = None,
    calendar_id_lookup: Any,
    delete_option: Optional[str] = "singleInstance",
) -> Response[Union[Any, DefaultError]]:
    """Delete Event (Calendar Event)

    Args:
        id (str): The ID of event to cancel/delete
        comment (Optional[str]): The message sent to the attendees/organizer of the deleted event
        calendar_id (Optional[str]): The ID of calendar in which respective event is present.
            Should be left empty for personal calendar.
        delete_option (Optional[str]): Indicates option for event deletion Default:
            'singleInstance'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
    """

    if not calendar_id and calendar_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/CalendarList"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if calendar_id_lookup in item["FullName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for calendar_id_lookup in CalendarList")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for calendar_id_lookup in CalendarList. Using the first match."
            )

        calendar_id = found_items[0]["ID"]

    kwargs = _get_kwargs(
        id=id,
        comment=comment,
        calendar_id=calendar_id,
        delete_option=delete_option,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: str,
    *,
    client: Union[AuthenticatedClient, Client],
    comment: Optional[str] = None,
    calendar_id: Optional[str] = None,
    calendar_id_lookup: Any,
    delete_option: Optional[str] = "singleInstance",
) -> Optional[Union[Any, DefaultError]]:
    """Delete Event (Calendar Event)

    Args:
        id (str): The ID of event to cancel/delete
        comment (Optional[str]): The message sent to the attendees/organizer of the deleted event
        calendar_id (Optional[str]): The ID of calendar in which respective event is present.
            Should be left empty for personal calendar.
        delete_option (Optional[str]): Indicates option for event deletion Default:
            'singleInstance'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            comment=comment,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            delete_option=delete_option,
        )
    ).parsed
