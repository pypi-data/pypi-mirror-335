from .archive_email import (
    archive_email as _archive_email,
    archive_email_async as _archive_email_async,
)
from ..models.archive_email_response import ArchiveEmailResponse
from ..models.default_error import DefaultError
from typing import cast
from .calendar import (
    create_event as _create_event,
    create_event_async as _create_event_async,
    get_event_by_id as _get_event_by_id,
    get_event_by_id_async as _get_event_by_id_async,
)
from ..models.create_event_body import CreateEventBody
from ..models.create_event_request import CreateEventRequest
from ..models.create_event_response import CreateEventResponse
from ..models.get_event_by_id_response import GetEventByIDResponse
from .message import (
    delete_email as _delete_email,
    delete_email_async as _delete_email_async,
)
from .delete_event import (
    delete_event as _delete_event,
    delete_event_async as _delete_event_async,
)
from .download_attachment import (
    download_attachment as _download_attachment,
    download_attachment_async as _download_attachment_async,
)
from ..models.download_attachment_response import DownloadAttachmentResponse
from ..types import File
from io import BytesIO
from .download_email import (
    download_email as _download_email,
    download_email_async as _download_email_async,
)
from ..models.download_email import DownloadEmail
from .forward_email import (
    forward_email as _forward_email,
    forward_email_async as _forward_email_async,
)
from ..models.forward_email_body import ForwardEmailBody
from ..models.forward_email_request import ForwardEmailRequest
from .forward_event import (
    forward_event as _forward_event,
    forward_event_async as _forward_event_async,
)
from ..models.forward_event_request import ForwardEventRequest
from .calendars import (
    get_calendars as _get_calendars,
    get_calendars_async as _get_calendars_async,
)
from ..models.get_calendars import GetCalendars
from .mail_folder import (
    get_email_folders as _get_email_folders,
    get_email_folders_async as _get_email_folders_async,
)
from ..models.get_email_folders import GetEmailFolders
from .list_emails import (
    get_email_list as _get_email_list,
    get_email_list_async as _get_email_list_async,
)
from ..models.get_email_list import GetEmailList
from .get_event_list import (
    get_event_list as _get_event_list,
    get_event_list_async as _get_event_list_async,
)
from ..models.get_event_list import GetEventList
from dateutil.parser import isoparse
import datetime
from .get_newest_email import (
    get_newest_email as _get_newest_email,
    get_newest_email_async as _get_newest_email_async,
)
from ..models.get_newest_email_response import GetNewestEmailResponse
from .mark_email_reador_unread import (
    mark_email_reador_unread as _mark_email_reador_unread,
    mark_email_reador_unread_async as _mark_email_reador_unread_async,
)
from ..models.mark_email_reador_unread_request import MarkEmailReadorUnreadRequest
from ..models.mark_email_reador_unread_response import MarkEmailReadorUnreadResponse
from .move_email import (
    move_email as _move_email,
    move_email_async as _move_email_async,
)
from ..models.move_email_request import MoveEmailRequest
from ..models.move_email_response import MoveEmailResponse
from .reply_to_email import (
    reply_to_email as _reply_to_email,
    reply_to_email_async as _reply_to_email_async,
)
from ..models.reply_to_email_body import ReplyToEmailBody
from ..models.reply_to_email_request import ReplyToEmailRequest
from .respondto_event_invitation import (
    respondto_event_invitation as _respondto_event_invitation,
    respondto_event_invitation_async as _respondto_event_invitation_async,
)
from ..models.respondto_event_invitation_request import RespondtoEventInvitationRequest
from ..models.respondto_event_invitation_response import (
    RespondtoEventInvitationResponse,
)
from .send_mail import (
    send_email as _send_email,
    send_email_async as _send_email_async,
)
from ..models.send_email_body import SendEmailBody
from ..models.send_email_request import SendEmailRequest
from ..models.send_email_response import SendEmailResponse
from .set_email_categories import (
    set_email_categories as _set_email_categories,
    set_email_categories_async as _set_email_categories_async,
)
from ..models.set_email_categories_request import SetEmailCategoriesRequest
from ..models.set_email_categories_response import SetEmailCategoriesResponse
from .turn_off_automatic_replies import (
    turn_off_automatic_replies as _turn_off_automatic_replies,
    turn_off_automatic_replies_async as _turn_off_automatic_replies_async,
)
from ..models.turn_off_automatic_replies_request import TurnOffAutomaticRepliesRequest
from ..models.turn_off_automatic_replies_response import TurnOffAutomaticRepliesResponse
from .turn_on_automatic_replies import (
    turn_on_automatic_replies as _turn_on_automatic_replies,
    turn_on_automatic_replies_async as _turn_on_automatic_replies_async,
)
from ..models.turn_on_automatic_replies_request import TurnOnAutomaticRepliesRequest
from ..models.turn_on_automatic_replies_response import TurnOnAutomaticRepliesResponse
from .update_event import (
    update_event as _update_event,
    update_event_async as _update_event_async,
)
from ..models.update_event_body import UpdateEventBody
from ..models.update_event_request import UpdateEventRequest
from ..models.update_event_response import UpdateEventResponse

from pydantic import Field
from typing import Any, Optional, Union

from ..client import Client
import httpx


class MicrosoftOutlook365:
    def __init__(self, *, instance_id: str, client: httpx.Client):
        base_url = str(client.base_url).rstrip("/")
        new_headers = {
            k: v for k, v in client.headers.items() if k not in ["content-type"]
        }
        new_client = httpx.Client(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        new_client_async = httpx.AsyncClient(
            base_url=base_url + f"/elements_/v3/element/instances/{instance_id}",
            headers=new_headers,
            timeout=100,
        )
        self.client = (
            Client(
                base_url="",  # this will be overridden by the base_url in the Client constructor
            )
            .set_httpx_client(new_client)
            .set_async_httpx_client(new_client_async)
        )

    def archive_email(
        self,
        *,
        id: str,
    ) -> Optional[Union[ArchiveEmailResponse, DefaultError]]:
        return _archive_email(
            client=self.client,
            id=id,
        )

    async def archive_email_async(
        self,
        *,
        id: str,
    ) -> Optional[Union[ArchiveEmailResponse, DefaultError]]:
        return await _archive_email_async(
            client=self.client,
            id=id,
        )

    def create_event(
        self,
        *,
        body: CreateEventBody,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        output_timezone: Optional[str] = None,
        output_timezone_lookup: Any,
    ) -> Optional[Union[CreateEventResponse, DefaultError]]:
        return _create_event(
            client=self.client,
            body=body,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            output_timezone=output_timezone,
            output_timezone_lookup=output_timezone_lookup,
        )

    async def create_event_async(
        self,
        *,
        body: CreateEventBody,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        output_timezone: Optional[str] = None,
        output_timezone_lookup: Any,
    ) -> Optional[Union[CreateEventResponse, DefaultError]]:
        return await _create_event_async(
            client=self.client,
            body=body,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            output_timezone=output_timezone,
            output_timezone_lookup=output_timezone_lookup,
        )

    def get_event_by_id(
        self,
        id: str,
        *,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        timezone: Optional[str] = None,
        timezone_lookup: Any,
    ) -> Optional[Union[DefaultError, GetEventByIDResponse]]:
        return _get_event_by_id(
            client=self.client,
            id=id,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            timezone=timezone,
            timezone_lookup=timezone_lookup,
        )

    async def get_event_by_id_async(
        self,
        id: str,
        *,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        timezone: Optional[str] = None,
        timezone_lookup: Any,
    ) -> Optional[Union[DefaultError, GetEventByIDResponse]]:
        return await _get_event_by_id_async(
            client=self.client,
            id=id,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            timezone=timezone,
            timezone_lookup=timezone_lookup,
        )

    def delete_email(
        self,
        id: str,
        *,
        permanently_delete: Optional[bool] = False,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_email(
            client=self.client,
            id=id,
            permanently_delete=permanently_delete,
        )

    async def delete_email_async(
        self,
        id: str,
        *,
        permanently_delete: Optional[bool] = False,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_email_async(
            client=self.client,
            id=id,
            permanently_delete=permanently_delete,
        )

    def delete_event(
        self,
        id: str,
        *,
        comment: Optional[str] = None,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        delete_option: Optional[str] = "singleInstance",
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_event(
            client=self.client,
            id=id,
            comment=comment,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            delete_option=delete_option,
        )

    async def delete_event_async(
        self,
        id: str,
        *,
        comment: Optional[str] = None,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        delete_option: Optional[str] = "singleInstance",
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_event_async(
            client=self.client,
            id=id,
            comment=comment,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            delete_option=delete_option,
        )

    def download_attachment(
        self,
        *,
        file_name: Optional[str] = None,
        id: str,
        exclude_inline_attachments: Optional[bool] = False,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_attachment(
            client=self.client,
            file_name=file_name,
            id=id,
            exclude_inline_attachments=exclude_inline_attachments,
        )

    async def download_attachment_async(
        self,
        *,
        file_name: Optional[str] = None,
        id: str,
        exclude_inline_attachments: Optional[bool] = False,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_attachment_async(
            client=self.client,
            file_name=file_name,
            id=id,
            exclude_inline_attachments=exclude_inline_attachments,
        )

    def download_email(
        self,
        *,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return _download_email(
            client=self.client,
            id=id,
        )

    async def download_email_async(
        self,
        *,
        id: str,
    ) -> Optional[Union[DefaultError, File]]:
        return await _download_email_async(
            client=self.client,
            id=id,
        )

    def forward_email(
        self,
        *,
        body: ForwardEmailBody,
        id: str,
        save_as_draft: Optional[bool] = True,
        timezone: Optional[str] = None,
        timezone_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _forward_email(
            client=self.client,
            body=body,
            id=id,
            save_as_draft=save_as_draft,
            timezone=timezone,
            timezone_lookup=timezone_lookup,
        )

    async def forward_email_async(
        self,
        *,
        body: ForwardEmailBody,
        id: str,
        save_as_draft: Optional[bool] = True,
        timezone: Optional[str] = None,
        timezone_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _forward_email_async(
            client=self.client,
            body=body,
            id=id,
            save_as_draft=save_as_draft,
            timezone=timezone,
            timezone_lookup=timezone_lookup,
        )

    def forward_event(
        self,
        *,
        body: ForwardEventRequest,
        id: str,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        apply_on_series: Optional[bool] = False,
    ) -> Optional[Union[Any, DefaultError]]:
        return _forward_event(
            client=self.client,
            body=body,
            id=id,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            apply_on_series=apply_on_series,
        )

    async def forward_event_async(
        self,
        *,
        body: ForwardEventRequest,
        id: str,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        apply_on_series: Optional[bool] = False,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _forward_event_async(
            client=self.client,
            body=body,
            id=id,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            apply_on_series=apply_on_series,
        )

    def get_calendars(
        self,
        *,
        where: Optional[str] = None,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetCalendars"]]]:
        return _get_calendars(
            client=self.client,
            where=where,
            page_size=page_size,
            next_page=next_page,
        )

    async def get_calendars_async(
        self,
        *,
        where: Optional[str] = None,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetCalendars"]]]:
        return await _get_calendars_async(
            client=self.client,
            where=where,
            page_size=page_size,
            next_page=next_page,
        )

    def get_email_folders(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        page: Optional[str] = None,
        filter_: Optional[str] = None,
        orderby: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
        shared_mailbox_address: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetEmailFolders"]]]:
        return _get_email_folders(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            page=page,
            filter_=filter_,
            orderby=orderby,
            parent_folder_id=parent_folder_id,
            shared_mailbox_address=shared_mailbox_address,
        )

    async def get_email_folders_async(
        self,
        *,
        page_size: Optional[int] = None,
        next_page: Optional[str] = None,
        page: Optional[str] = None,
        filter_: Optional[str] = None,
        orderby: Optional[str] = None,
        parent_folder_id: Optional[str] = None,
        shared_mailbox_address: Optional[str] = None,
    ) -> Optional[Union[DefaultError, list["GetEmailFolders"]]]:
        return await _get_email_folders_async(
            client=self.client,
            page_size=page_size,
            next_page=next_page,
            page=page,
            filter_=filter_,
            orderby=orderby,
            parent_folder_id=parent_folder_id,
            shared_mailbox_address=shared_mailbox_address,
        )

    def get_email_list(
        self,
        *,
        un_read_only: Optional[bool] = False,
        filter_: Optional[str] = None,
        limit: Optional[str] = "100",
        importance: Optional[str] = None,
        parent_folder_id: str,
        parent_folder_id_lookup: Any,
        with_attachments_only: Optional[bool] = False,
        include_subfolders: Optional[bool] = False,
        mark_as_read: Optional[bool] = None,
    ) -> Optional[Union[DefaultError, list["GetEmailList"]]]:
        return _get_email_list(
            client=self.client,
            un_read_only=un_read_only,
            filter_=filter_,
            limit=limit,
            importance=importance,
            parent_folder_id=parent_folder_id,
            parent_folder_id_lookup=parent_folder_id_lookup,
            with_attachments_only=with_attachments_only,
            include_subfolders=include_subfolders,
            mark_as_read=mark_as_read,
        )

    async def get_email_list_async(
        self,
        *,
        un_read_only: Optional[bool] = False,
        filter_: Optional[str] = None,
        limit: Optional[str] = "100",
        importance: Optional[str] = None,
        parent_folder_id: str,
        parent_folder_id_lookup: Any,
        with_attachments_only: Optional[bool] = False,
        include_subfolders: Optional[bool] = False,
        mark_as_read: Optional[bool] = None,
    ) -> Optional[Union[DefaultError, list["GetEmailList"]]]:
        return await _get_email_list_async(
            client=self.client,
            un_read_only=un_read_only,
            filter_=filter_,
            limit=limit,
            importance=importance,
            parent_folder_id=parent_folder_id,
            parent_folder_id_lookup=parent_folder_id_lookup,
            with_attachments_only=with_attachments_only,
            include_subfolders=include_subfolders,
            mark_as_read=mark_as_read,
        )

    def get_event_list(
        self,
        *,
        until: datetime.datetime,
        filter_: Optional[str] = None,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        size: Optional[str] = "50",
        from_: datetime.datetime,
        output_timezone: Optional[str] = None,
        output_timezone_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetEventList"]]]:
        return _get_event_list(
            client=self.client,
            until=until,
            filter_=filter_,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            size=size,
            from_=from_,
            output_timezone=output_timezone,
            output_timezone_lookup=output_timezone_lookup,
        )

    async def get_event_list_async(
        self,
        *,
        until: datetime.datetime,
        filter_: Optional[str] = None,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        size: Optional[str] = "50",
        from_: datetime.datetime,
        output_timezone: Optional[str] = None,
        output_timezone_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetEventList"]]]:
        return await _get_event_list_async(
            client=self.client,
            until=until,
            filter_=filter_,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            size=size,
            from_=from_,
            output_timezone=output_timezone,
            output_timezone_lookup=output_timezone_lookup,
        )

    def get_newest_email(
        self,
        *,
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
        return _get_newest_email(
            client=self.client,
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

    async def get_newest_email_async(
        self,
        *,
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
        return await _get_newest_email_async(
            client=self.client,
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

    def mark_email_reador_unread(
        self,
        id: str,
        *,
        body: MarkEmailReadorUnreadRequest,
    ) -> Optional[Union[DefaultError, MarkEmailReadorUnreadResponse]]:
        return _mark_email_reador_unread(
            client=self.client,
            id=id,
            body=body,
        )

    async def mark_email_reador_unread_async(
        self,
        id: str,
        *,
        body: MarkEmailReadorUnreadRequest,
    ) -> Optional[Union[DefaultError, MarkEmailReadorUnreadResponse]]:
        return await _mark_email_reador_unread_async(
            client=self.client,
            id=id,
            body=body,
        )

    def move_email(
        self,
        id: str,
        *,
        body: MoveEmailRequest,
    ) -> Optional[Union[DefaultError, MoveEmailResponse]]:
        return _move_email(
            client=self.client,
            id=id,
            body=body,
        )

    async def move_email_async(
        self,
        id: str,
        *,
        body: MoveEmailRequest,
    ) -> Optional[Union[DefaultError, MoveEmailResponse]]:
        return await _move_email_async(
            client=self.client,
            id=id,
            body=body,
        )

    def reply_to_email(
        self,
        *,
        body: ReplyToEmailBody,
        save_as_draft: Optional[bool] = True,
        id: str,
        reply_to_all: Optional[bool] = False,
        timezone: Optional[str] = None,
        timezone_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _reply_to_email(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
            id=id,
            reply_to_all=reply_to_all,
            timezone=timezone,
            timezone_lookup=timezone_lookup,
        )

    async def reply_to_email_async(
        self,
        *,
        body: ReplyToEmailBody,
        save_as_draft: Optional[bool] = True,
        id: str,
        reply_to_all: Optional[bool] = False,
        timezone: Optional[str] = None,
        timezone_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _reply_to_email_async(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
            id=id,
            reply_to_all=reply_to_all,
            timezone=timezone,
            timezone_lookup=timezone_lookup,
        )

    def respondto_event_invitation(
        self,
        *,
        body: RespondtoEventInvitationRequest,
        response: str = "accept",
        apply_on_series: Optional[bool] = False,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        id: str,
    ) -> Optional[Union[DefaultError, RespondtoEventInvitationResponse]]:
        return _respondto_event_invitation(
            client=self.client,
            body=body,
            response=response,
            apply_on_series=apply_on_series,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            id=id,
        )

    async def respondto_event_invitation_async(
        self,
        *,
        body: RespondtoEventInvitationRequest,
        response: str = "accept",
        apply_on_series: Optional[bool] = False,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        id: str,
    ) -> Optional[Union[DefaultError, RespondtoEventInvitationResponse]]:
        return await _respondto_event_invitation_async(
            client=self.client,
            body=body,
            response=response,
            apply_on_series=apply_on_series,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            id=id,
        )

    def send_email(
        self,
        *,
        body: SendEmailBody,
        save_as_draft: Optional[bool] = True,
    ) -> Optional[Union[DefaultError, SendEmailResponse]]:
        return _send_email(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
        )

    async def send_email_async(
        self,
        *,
        body: SendEmailBody,
        save_as_draft: Optional[bool] = True,
    ) -> Optional[Union[DefaultError, SendEmailResponse]]:
        return await _send_email_async(
            client=self.client,
            body=body,
            save_as_draft=save_as_draft,
        )

    def set_email_categories(
        self,
        id: str,
        *,
        body: SetEmailCategoriesRequest,
    ) -> Optional[Union[DefaultError, SetEmailCategoriesResponse]]:
        return _set_email_categories(
            client=self.client,
            id=id,
            body=body,
        )

    async def set_email_categories_async(
        self,
        id: str,
        *,
        body: SetEmailCategoriesRequest,
    ) -> Optional[Union[DefaultError, SetEmailCategoriesResponse]]:
        return await _set_email_categories_async(
            client=self.client,
            id=id,
            body=body,
        )

    def turn_off_automatic_replies(
        self,
        *,
        body: TurnOffAutomaticRepliesRequest,
    ) -> Optional[Union[DefaultError, TurnOffAutomaticRepliesResponse]]:
        return _turn_off_automatic_replies(
            client=self.client,
            body=body,
        )

    async def turn_off_automatic_replies_async(
        self,
        *,
        body: TurnOffAutomaticRepliesRequest,
    ) -> Optional[Union[DefaultError, TurnOffAutomaticRepliesResponse]]:
        return await _turn_off_automatic_replies_async(
            client=self.client,
            body=body,
        )

    def turn_on_automatic_replies(
        self,
        *,
        body: TurnOnAutomaticRepliesRequest,
    ) -> Optional[Union[DefaultError, TurnOnAutomaticRepliesResponse]]:
        return _turn_on_automatic_replies(
            client=self.client,
            body=body,
        )

    async def turn_on_automatic_replies_async(
        self,
        *,
        body: TurnOnAutomaticRepliesRequest,
    ) -> Optional[Union[DefaultError, TurnOnAutomaticRepliesResponse]]:
        return await _turn_on_automatic_replies_async(
            client=self.client,
            body=body,
        )

    def update_event(
        self,
        id: str,
        *,
        body: UpdateEventBody,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        output_timezone: Optional[str] = None,
        output_timezone_lookup: Any,
        remove_attachment_id: Optional[str] = None,
        change_attachment: Optional[str] = None,
    ) -> Optional[Union[DefaultError, UpdateEventResponse]]:
        return _update_event(
            client=self.client,
            id=id,
            body=body,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            output_timezone=output_timezone,
            output_timezone_lookup=output_timezone_lookup,
            remove_attachment_id=remove_attachment_id,
            change_attachment=change_attachment,
        )

    async def update_event_async(
        self,
        id: str,
        *,
        body: UpdateEventBody,
        calendar_id: Optional[str] = None,
        calendar_id_lookup: Any,
        output_timezone: Optional[str] = None,
        output_timezone_lookup: Any,
        remove_attachment_id: Optional[str] = None,
        change_attachment: Optional[str] = None,
    ) -> Optional[Union[DefaultError, UpdateEventResponse]]:
        return await _update_event_async(
            client=self.client,
            id=id,
            body=body,
            calendar_id=calendar_id,
            calendar_id_lookup=calendar_id_lookup,
            output_timezone=output_timezone,
            output_timezone_lookup=output_timezone_lookup,
            remove_attachment_id=remove_attachment_id,
            change_attachment=change_attachment,
        )
