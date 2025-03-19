from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_newest_email_response import GetNewestEmailResponse


def _get_kwargs(
    *,
    parent_folder_id: str,
    importance: Optional[str] = "any",
    order_by: Optional[str] = "receivedDateTime desc",
    top: Optional[str] = "1",
    un_read_only: Optional[bool] = False,
    with_attachments_only: Optional[bool] = False,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["parentFolderId"] = parent_folder_id

    params["importance"] = importance

    params["orderBy"] = order_by

    params["top"] = top

    params["unReadOnly"] = un_read_only

    params["withAttachmentsOnly"] = with_attachments_only

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/getNewestEmail",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, GetNewestEmailResponse]]:
    if response.status_code == 200:
        response_200 = GetNewestEmailResponse.from_dict(response.json())

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
) -> Response[Union[DefaultError, GetNewestEmailResponse]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    importance: Optional[str] = "any",
    importance_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    order_by_lookup: Any,
    top: Optional[str] = "1",
    top_lookup: Any,
    un_read_only: Optional[bool] = False,
    un_read_only_lookup: Any,
    with_attachments_only: Optional[bool] = False,
    with_attachments_only_lookup: Any,
) -> Response[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        parent_folder_id (str):
        importance (Optional[str]):  Default: 'any'.
        order_by (Optional[str]):  Default: 'receivedDateTime desc'.
        top (Optional[str]):  Default: '1'.
        un_read_only (Optional[bool]):  Default: False.
        with_attachments_only (Optional[bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetNewestEmailResponse]]
    """

    if not parent_folder_id and parent_folder_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get",
            url=f"/MailFolders?sharedMailboxAddress={sharedMailboxAddress}",
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if parent_folder_id_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for parent_folder_id_lookup in MailFolder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for parent_folder_id_lookup in MailFolder. Using the first match."
            )

        parent_folder_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        parent_folder_id=parent_folder_id,
        importance=importance,
        order_by=order_by,
        top=top,
        un_read_only=un_read_only,
        with_attachments_only=with_attachments_only,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    importance: Optional[str] = "any",
    importance_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    order_by_lookup: Any,
    top: Optional[str] = "1",
    top_lookup: Any,
    un_read_only: Optional[bool] = False,
    un_read_only_lookup: Any,
    with_attachments_only: Optional[bool] = False,
    with_attachments_only_lookup: Any,
) -> Optional[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        parent_folder_id (str):
        importance (Optional[str]):  Default: 'any'.
        order_by (Optional[str]):  Default: 'receivedDateTime desc'.
        top (Optional[str]):  Default: '1'.
        un_read_only (Optional[bool]):  Default: False.
        with_attachments_only (Optional[bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetNewestEmailResponse]
    """

    return sync_detailed(
        client=client,
        parent_folder_id=parent_folder_id,
        parent_folder_id_lookup=parent_folder_id_lookup,
        importance=importance,
        importance_lookup=importance_lookup,
        order_by=order_by,
        order_by_lookup=order_by_lookup,
        top=top,
        top_lookup=top_lookup,
        un_read_only=un_read_only,
        un_read_only_lookup=un_read_only_lookup,
        with_attachments_only=with_attachments_only,
        with_attachments_only_lookup=with_attachments_only_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    importance: Optional[str] = "any",
    importance_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    order_by_lookup: Any,
    top: Optional[str] = "1",
    top_lookup: Any,
    un_read_only: Optional[bool] = False,
    un_read_only_lookup: Any,
    with_attachments_only: Optional[bool] = False,
    with_attachments_only_lookup: Any,
) -> Response[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        parent_folder_id (str):
        importance (Optional[str]):  Default: 'any'.
        order_by (Optional[str]):  Default: 'receivedDateTime desc'.
        top (Optional[str]):  Default: '1'.
        un_read_only (Optional[bool]):  Default: False.
        with_attachments_only (Optional[bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetNewestEmailResponse]]
    """

    if not parent_folder_id and parent_folder_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get",
            url=f"/MailFolders?sharedMailboxAddress={sharedMailboxAddress}",
        )
        lookup_response = lookup_response_raw.json()

        found_items = []
        for item in lookup_response:
            if parent_folder_id_lookup in item["displayName"]:
                found_items.append(item)

        if not found_items:
            raise ValueError(
                "No matches found for parent_folder_id_lookup in MailFolder"
            )
        if len(found_items) > 1:
            print(
                "Warning: Multiple matches found for parent_folder_id_lookup in MailFolder. Using the first match."
            )

        parent_folder_id = found_items[0]["id"]

    kwargs = _get_kwargs(
        parent_folder_id=parent_folder_id,
        importance=importance,
        order_by=order_by,
        top=top,
        un_read_only=un_read_only,
        with_attachments_only=with_attachments_only,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    importance: Optional[str] = "any",
    importance_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    order_by_lookup: Any,
    top: Optional[str] = "1",
    top_lookup: Any,
    un_read_only: Optional[bool] = False,
    un_read_only_lookup: Any,
    with_attachments_only: Optional[bool] = False,
    with_attachments_only_lookup: Any,
) -> Optional[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        parent_folder_id (str):
        importance (Optional[str]):  Default: 'any'.
        order_by (Optional[str]):  Default: 'receivedDateTime desc'.
        top (Optional[str]):  Default: '1'.
        un_read_only (Optional[bool]):  Default: False.
        with_attachments_only (Optional[bool]):  Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetNewestEmailResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            parent_folder_id=parent_folder_id,
            parent_folder_id_lookup=parent_folder_id_lookup,
            importance=importance,
            importance_lookup=importance_lookup,
            order_by=order_by,
            order_by_lookup=order_by_lookup,
            top=top,
            top_lookup=top_lookup,
            un_read_only=un_read_only,
            un_read_only_lookup=un_read_only_lookup,
            with_attachments_only=with_attachments_only,
            with_attachments_only_lookup=with_attachments_only_lookup,
        )
    ).parsed
