from http import HTTPStatus
from typing import Any, Optional, Union, cast

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.forward_email_body import ForwardEmailBody


def _get_kwargs(
    *,
    body: ForwardEmailBody,
    id: str,
    save_as_draft: Optional[bool] = True,
    timezone: Optional[str] = None,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["id"] = id

    params["saveAsDraft"] = save_as_draft

    params["timezone"] = timezone

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/forwardEmail",
        "params": params,
    }

    _body = body.to_multipart()

    _kwargs["files"] = _body

    _kwargs["headers"] = headers
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
    *,
    client: Union[AuthenticatedClient, Client],
    body: ForwardEmailBody,
    id: str,
    save_as_draft: Optional[bool] = True,
    timezone: Optional[str] = None,
    timezone_lookup: Any,
) -> Response[Union[Any, DefaultError]]:
    """Forward Email

     Forward Email

    Args:
        id (str): The ID of email to forward
        save_as_draft (Optional[bool]): Save as Draft Default: True.
        timezone (Optional[str]): Set the timezone for forwarded email messages. If not specified,
            the default timezone will be UTC.
        body (ForwardEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
    """

    if not timezone and timezone_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/timezones"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if timezone_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for timezone_lookup in timezones")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for timezone_lookup in timezones. Using the first match."
            )

        timezone = found_items[0]["alias"]

    kwargs = _get_kwargs(
        body=body,
        id=id,
        save_as_draft=save_as_draft,
        timezone=timezone,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ForwardEmailBody,
    id: str,
    save_as_draft: Optional[bool] = True,
    timezone: Optional[str] = None,
    timezone_lookup: Any,
) -> Optional[Union[Any, DefaultError]]:
    """Forward Email

     Forward Email

    Args:
        id (str): The ID of email to forward
        save_as_draft (Optional[bool]): Save as Draft Default: True.
        timezone (Optional[str]): Set the timezone for forwarded email messages. If not specified,
            the default timezone will be UTC.
        body (ForwardEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return sync_detailed(
        client=client,
        body=body,
        id=id,
        save_as_draft=save_as_draft,
        timezone=timezone,
        timezone_lookup=timezone_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ForwardEmailBody,
    id: str,
    save_as_draft: Optional[bool] = True,
    timezone: Optional[str] = None,
    timezone_lookup: Any,
) -> Response[Union[Any, DefaultError]]:
    """Forward Email

     Forward Email

    Args:
        id (str): The ID of email to forward
        save_as_draft (Optional[bool]): Save as Draft Default: True.
        timezone (Optional[str]): Set the timezone for forwarded email messages. If not specified,
            the default timezone will be UTC.
        body (ForwardEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[Any, DefaultError]]
    """

    if not timezone and timezone_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/timezones"
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if timezone_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError("No matches found for timezone_lookup in timezones")
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for timezone_lookup in timezones. Using the first match."
            )

        timezone = found_items[0]["alias"]

    kwargs = _get_kwargs(
        body=body,
        id=id,
        save_as_draft=save_as_draft,
        timezone=timezone,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ForwardEmailBody,
    id: str,
    save_as_draft: Optional[bool] = True,
    timezone: Optional[str] = None,
    timezone_lookup: Any,
) -> Optional[Union[Any, DefaultError]]:
    """Forward Email

     Forward Email

    Args:
        id (str): The ID of email to forward
        save_as_draft (Optional[bool]): Save as Draft Default: True.
        timezone (Optional[str]): Set the timezone for forwarded email messages. If not specified,
            the default timezone will be UTC.
        body (ForwardEmailBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[Any, DefaultError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            id=id,
            save_as_draft=save_as_draft,
            timezone=timezone,
            timezone_lookup=timezone_lookup,
        )
    ).parsed
