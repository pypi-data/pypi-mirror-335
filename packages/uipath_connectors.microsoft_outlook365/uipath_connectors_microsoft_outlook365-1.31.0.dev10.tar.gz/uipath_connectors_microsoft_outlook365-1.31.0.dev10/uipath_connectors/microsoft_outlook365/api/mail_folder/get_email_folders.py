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
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    page: Optional[str] = None,
    filter_: Optional[str] = None,
    orderby: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    shared_mailbox_address: Optional[str] = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["pageSize"] = page_size

    params["nextPage"] = next_page

    params["page"] = page

    params["filter"] = filter_

    params["orderby"] = orderby

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
        for response_200_item_data in _response_200:
            response_200_item = GetEmailFolders.from_dict(response_200_item_data)

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
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    page: Optional[str] = None,
    filter_: Optional[str] = None,
    orderby: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    shared_mailbox_address: Optional[str] = None,
) -> Response[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders List

     Returns list of folders available to user in their mailbox

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        page (Optional[str]): The next page token, taken from the response headers 'elements-next-
            page-token'
        filter_ (Optional[str]): The OData query parameter to retrieve a subset of the MailFolders
        orderby (Optional[str]): The OData query parameter to order the MailFolders by
        parent_folder_id (Optional[str]): The Parent folder ID to get the child folders
        shared_mailbox_address (Optional[str]): Shared mailbox's email address for polling

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetEmailFolders']]]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        page=page,
        filter_=filter_,
        orderby=orderby,
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
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    page: Optional[str] = None,
    filter_: Optional[str] = None,
    orderby: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    shared_mailbox_address: Optional[str] = None,
) -> Optional[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders List

     Returns list of folders available to user in their mailbox

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        page (Optional[str]): The next page token, taken from the response headers 'elements-next-
            page-token'
        filter_ (Optional[str]): The OData query parameter to retrieve a subset of the MailFolders
        orderby (Optional[str]): The OData query parameter to order the MailFolders by
        parent_folder_id (Optional[str]): The Parent folder ID to get the child folders
        shared_mailbox_address (Optional[str]): Shared mailbox's email address for polling

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetEmailFolders']]
    """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_page=next_page,
        page=page,
        filter_=filter_,
        orderby=orderby,
        parent_folder_id=parent_folder_id,
        shared_mailbox_address=shared_mailbox_address,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    page: Optional[str] = None,
    filter_: Optional[str] = None,
    orderby: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    shared_mailbox_address: Optional[str] = None,
) -> Response[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders List

     Returns list of folders available to user in their mailbox

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        page (Optional[str]): The next page token, taken from the response headers 'elements-next-
            page-token'
        filter_ (Optional[str]): The OData query parameter to retrieve a subset of the MailFolders
        orderby (Optional[str]): The OData query parameter to order the MailFolders by
        parent_folder_id (Optional[str]): The Parent folder ID to get the child folders
        shared_mailbox_address (Optional[str]): Shared mailbox's email address for polling

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[DefaultError, list['GetEmailFolders']]]
    """

    kwargs = _get_kwargs(
        page_size=page_size,
        next_page=next_page,
        page=page,
        filter_=filter_,
        orderby=orderby,
        parent_folder_id=parent_folder_id,
        shared_mailbox_address=shared_mailbox_address,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    page_size: Optional[int] = None,
    next_page: Optional[str] = None,
    page: Optional[str] = None,
    filter_: Optional[str] = None,
    orderby: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    shared_mailbox_address: Optional[str] = None,
) -> Optional[Union[DefaultError, list["GetEmailFolders"]]]:
    """Get Email Folders List

     Returns list of folders available to user in their mailbox

    Args:
        page_size (Optional[int]): The number of resources to return in a given page
        next_page (Optional[str]): The next page cursor, taken from the response header:
            `elements-next-page-token`
        page (Optional[str]): The next page token, taken from the response headers 'elements-next-
            page-token'
        filter_ (Optional[str]): The OData query parameter to retrieve a subset of the MailFolders
        orderby (Optional[str]): The OData query parameter to order the MailFolders by
        parent_folder_id (Optional[str]): The Parent folder ID to get the child folders
        shared_mailbox_address (Optional[str]): Shared mailbox's email address for polling

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[DefaultError, list['GetEmailFolders']]
    """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_page=next_page,
            page=page,
            filter_=filter_,
            orderby=orderby,
            parent_folder_id=parent_folder_id,
            shared_mailbox_address=shared_mailbox_address,
        )
    ).parsed
