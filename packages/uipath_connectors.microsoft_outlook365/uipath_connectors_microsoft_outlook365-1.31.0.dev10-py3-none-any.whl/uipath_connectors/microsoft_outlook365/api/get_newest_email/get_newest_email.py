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
    filter_: Optional[str] = None,
    with_attachments_only: Optional[bool] = False,
    mark_as_read: Optional[bool] = False,
    parent_folder_id: str,
    order_by: Optional[str] = "receivedDateTime desc",
    un_read_only: Optional[bool] = False,
    top: Optional[str] = "1",
    importance: Optional[str] = "any",
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["filter"] = filter_

    params["withAttachmentsOnly"] = with_attachments_only

    params["markAsRead"] = mark_as_read

    params["parentFolderId"] = parent_folder_id

    params["orderBy"] = order_by

    params["unReadOnly"] = un_read_only

    params["top"] = top

    params["importance"] = importance

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
    filter_: Optional[str] = None,
    with_attachments_only: Optional[bool] = False,
    mark_as_read: Optional[bool] = False,
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    un_read_only: Optional[bool] = False,
    top: Optional[str] = "1",
    importance: Optional[str] = "any",
) -> Response[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        filter_ (Optional[str]): The OData query parameter to retrieve an email
        with_attachments_only (Optional[bool]): With attachments only Default: False.
        mark_as_read (Optional[bool]): Indicates whether to mark the retrieved email as read
            Default: False.
        parent_folder_id (str): Email Folder
        order_by (Optional[str]): OrderBy Default: 'receivedDateTime desc'.
        un_read_only (Optional[bool]): Indicates whether to consider unread only Default: False.
        top (Optional[str]): Top Default: '1'.
        importance (Optional[str]): Importance of the email Default: 'any'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetNewestEmailResponse]]
    """

    if not parent_folder_id and parent_folder_id_lookup:
        lookup_response_raw = client.get_httpx_client().request(
            method="get", url="/MailFolders"
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
        filter_=filter_,
        with_attachments_only=with_attachments_only,
        mark_as_read=mark_as_read,
        parent_folder_id=parent_folder_id,
        order_by=order_by,
        un_read_only=un_read_only,
        top=top,
        importance=importance,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    filter_: Optional[str] = None,
    with_attachments_only: Optional[bool] = False,
    mark_as_read: Optional[bool] = False,
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    un_read_only: Optional[bool] = False,
    top: Optional[str] = "1",
    importance: Optional[str] = "any",
) -> Optional[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        filter_ (Optional[str]): The OData query parameter to retrieve an email
        with_attachments_only (Optional[bool]): With attachments only Default: False.
        mark_as_read (Optional[bool]): Indicates whether to mark the retrieved email as read
            Default: False.
        parent_folder_id (str): Email Folder
        order_by (Optional[str]): OrderBy Default: 'receivedDateTime desc'.
        un_read_only (Optional[bool]): Indicates whether to consider unread only Default: False.
        top (Optional[str]): Top Default: '1'.
        importance (Optional[str]): Importance of the email Default: 'any'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetNewestEmailResponse]
    """

    return sync_detailed(
        client=client,
        filter_=filter_,
        with_attachments_only=with_attachments_only,
        mark_as_read=mark_as_read,
        parent_folder_id=parent_folder_id,
        parent_folder_id_lookup=parent_folder_id_lookup,
        order_by=order_by,
        un_read_only=un_read_only,
        top=top,
        importance=importance,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    filter_: Optional[str] = None,
    with_attachments_only: Optional[bool] = False,
    mark_as_read: Optional[bool] = False,
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    un_read_only: Optional[bool] = False,
    top: Optional[str] = "1",
    importance: Optional[str] = "any",
) -> Response[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        filter_ (Optional[str]): The OData query parameter to retrieve an email
        with_attachments_only (Optional[bool]): With attachments only Default: False.
        mark_as_read (Optional[bool]): Indicates whether to mark the retrieved email as read
            Default: False.
        parent_folder_id (str): Email Folder
        order_by (Optional[str]): OrderBy Default: 'receivedDateTime desc'.
        un_read_only (Optional[bool]): Indicates whether to consider unread only Default: False.
        top (Optional[str]): Top Default: '1'.
        importance (Optional[str]): Importance of the email Default: 'any'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, GetNewestEmailResponse]]
    """

    if not parent_folder_id and parent_folder_id_lookup:
        lookup_response_raw = await client.get_async_httpx_client().request(
            method="get", url="/MailFolders"
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
        filter_=filter_,
        with_attachments_only=with_attachments_only,
        mark_as_read=mark_as_read,
        parent_folder_id=parent_folder_id,
        order_by=order_by,
        un_read_only=un_read_only,
        top=top,
        importance=importance,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    filter_: Optional[str] = None,
    with_attachments_only: Optional[bool] = False,
    mark_as_read: Optional[bool] = False,
    parent_folder_id: str,
    parent_folder_id_lookup: Any,
    order_by: Optional[str] = "receivedDateTime desc",
    un_read_only: Optional[bool] = False,
    top: Optional[str] = "1",
    importance: Optional[str] = "any",
) -> Optional[Union[DefaultError, GetNewestEmailResponse]]:
    """Get Newest Email

     Get Newest Email

    Args:
        filter_ (Optional[str]): The OData query parameter to retrieve an email
        with_attachments_only (Optional[bool]): With attachments only Default: False.
        mark_as_read (Optional[bool]): Indicates whether to mark the retrieved email as read
            Default: False.
        parent_folder_id (str): Email Folder
        order_by (Optional[str]): OrderBy Default: 'receivedDateTime desc'.
        un_read_only (Optional[bool]): Indicates whether to consider unread only Default: False.
        top (Optional[str]): Top Default: '1'.
        importance (Optional[str]): Importance of the email Default: 'any'.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, GetNewestEmailResponse]
    """

    return (
        await asyncio_detailed(
            client=client,
            filter_=filter_,
            with_attachments_only=with_attachments_only,
            mark_as_read=mark_as_read,
            parent_folder_id=parent_folder_id,
            parent_folder_id_lookup=parent_folder_id_lookup,
            order_by=order_by,
            un_read_only=un_read_only,
            top=top,
            importance=importance,
        )
    ).parsed
