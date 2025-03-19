from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ...client import AuthenticatedClient, Client
from ...types import Response
from ... import errors

from ...models.default_error import DefaultError
from ...models.get_email_folders import GetEmailFolders


def _get_kwargs(
    *,
    fields: Optional[str] = None,
    filter_: Optional[str] = None,
    next_page: Optional[str] = None,
    orderby: Optional[str] = None,
    page: Optional[str] = None,
    page_size: Optional[int] = None,
    parent_folder_id: Optional[str] = None,
    shared_mailbox_address: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["fields"] = fields

    params["filter"] = filter_

    params["nextPage"] = next_page

    params["orderby"] = orderby

    params["page"] = page

    params["pageSize"] = page_size

    params["parentFolderId"] = parent_folder_id

    params["sharedMailboxAddress"] = shared_mailbox_address

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/MailFolders",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[DefaultError, list["GetEmailFolders"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for componentsschemas_get_email_folders_list_item_data in _response_200:
            componentsschemas_get_email_folders_list_item = GetEmailFolders.from_dict(
                componentsschemas_get_email_folders_list_item_data
            )

            response_200.append(componentsschemas_get_email_folders_list_item)

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
) -> Response[Union[DefaultError, list["GetEmailFolders"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    filter_: Optional[str] = None,
    filter__lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    orderby: Optional[str] = None,
    orderby_lookup: Any,
    page: Optional[str] = None,
    page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    parent_folder_id: Optional[str] = None,
    parent_folder_id_lookup: Any,
    shared_mailbox_address: Optional[str] = None,
    shared_mailbox_address_lookup: Any,
) -> Response[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders

     Returns list of folders available to user in their mailbox

    Args:
        fields (Optional[str]):
        filter_ (Optional[str]):
        next_page (Optional[str]):
        orderby (Optional[str]):
        page (Optional[str]):
        page_size (Optional[int]):
        parent_folder_id (Optional[str]):
        shared_mailbox_address (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetEmailFolders']]]
    """

    kwargs = _get_kwargs(
        fields=fields,
        filter_=filter_,
        next_page=next_page,
        orderby=orderby,
        page=page,
        page_size=page_size,
        parent_folder_id=parent_folder_id,
        shared_mailbox_address=shared_mailbox_address,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    filter_: Optional[str] = None,
    filter__lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    orderby: Optional[str] = None,
    orderby_lookup: Any,
    page: Optional[str] = None,
    page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    parent_folder_id: Optional[str] = None,
    parent_folder_id_lookup: Any,
    shared_mailbox_address: Optional[str] = None,
    shared_mailbox_address_lookup: Any,
) -> Optional[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders

     Returns list of folders available to user in their mailbox

    Args:
        fields (Optional[str]):
        filter_ (Optional[str]):
        next_page (Optional[str]):
        orderby (Optional[str]):
        page (Optional[str]):
        page_size (Optional[int]):
        parent_folder_id (Optional[str]):
        shared_mailbox_address (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetEmailFolders']]
    """

    return sync_detailed(
        client=client,
        fields=fields,
        fields_lookup=fields_lookup,
        filter_=filter_,
        filter__lookup=filter__lookup,
        next_page=next_page,
        next_page_lookup=next_page_lookup,
        orderby=orderby,
        orderby_lookup=orderby_lookup,
        page=page,
        page_lookup=page_lookup,
        page_size=page_size,
        page_size_lookup=page_size_lookup,
        parent_folder_id=parent_folder_id,
        parent_folder_id_lookup=parent_folder_id_lookup,
        shared_mailbox_address=shared_mailbox_address,
        shared_mailbox_address_lookup=shared_mailbox_address_lookup,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    filter_: Optional[str] = None,
    filter__lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    orderby: Optional[str] = None,
    orderby_lookup: Any,
    page: Optional[str] = None,
    page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    parent_folder_id: Optional[str] = None,
    parent_folder_id_lookup: Any,
    shared_mailbox_address: Optional[str] = None,
    shared_mailbox_address_lookup: Any,
) -> Response[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders

     Returns list of folders available to user in their mailbox

    Args:
        fields (Optional[str]):
        filter_ (Optional[str]):
        next_page (Optional[str]):
        orderby (Optional[str]):
        page (Optional[str]):
        page_size (Optional[int]):
        parent_folder_id (Optional[str]):
        shared_mailbox_address (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetEmailFolders']]]
    """

    kwargs = _get_kwargs(
        fields=fields,
        filter_=filter_,
        next_page=next_page,
        orderby=orderby,
        page=page,
        page_size=page_size,
        parent_folder_id=parent_folder_id,
        shared_mailbox_address=shared_mailbox_address,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    fields: Optional[str] = None,
    fields_lookup: Any,
    filter_: Optional[str] = None,
    filter__lookup: Any,
    next_page: Optional[str] = None,
    next_page_lookup: Any,
    orderby: Optional[str] = None,
    orderby_lookup: Any,
    page: Optional[str] = None,
    page_lookup: Any,
    page_size: Optional[int] = None,
    page_size_lookup: Any,
    parent_folder_id: Optional[str] = None,
    parent_folder_id_lookup: Any,
    shared_mailbox_address: Optional[str] = None,
    shared_mailbox_address_lookup: Any,
) -> Optional[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders

     Returns list of folders available to user in their mailbox

    Args:
        fields (Optional[str]):
        filter_ (Optional[str]):
        next_page (Optional[str]):
        orderby (Optional[str]):
        page (Optional[str]):
        page_size (Optional[int]):
        parent_folder_id (Optional[str]):
        shared_mailbox_address (Optional[str]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetEmailFolders']]
    """

    return (
        await asyncio_detailed(
            client=client,
            fields=fields,
            fields_lookup=fields_lookup,
            filter_=filter_,
            filter__lookup=filter__lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            orderby=orderby,
            orderby_lookup=orderby_lookup,
            page=page,
            page_lookup=page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            parent_folder_id=parent_folder_id,
            parent_folder_id_lookup=parent_folder_id_lookup,
            shared_mailbox_address=shared_mailbox_address,
            shared_mailbox_address_lookup=shared_mailbox_address_lookup,
        )
    ).parsed
