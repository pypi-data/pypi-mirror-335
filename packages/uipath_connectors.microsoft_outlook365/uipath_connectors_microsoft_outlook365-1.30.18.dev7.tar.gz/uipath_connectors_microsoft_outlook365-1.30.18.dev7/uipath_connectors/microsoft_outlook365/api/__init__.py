from .download_email import (
    download_email as _download_email,
    download_email_async as _download_email_async,
)
from ..models.default_error import DefaultError
from typing import cast
from .calendar_list import (
    get_calendar_list as _get_calendar_list,
    get_calendar_list_async as _get_calendar_list_async,
)
from ..models.get_calendar_list import GetCalendarList
from .calendars import (
    get_calendars as _get_calendars,
    get_calendars_async as _get_calendars_async,
)
from ..models.get_calendars import GetCalendars
from .forward_event import (
    forward_event as _forward_event,
    forward_event_async as _forward_event_async,
)
from ..models.forward_event_request import ForwardEventRequest
from .archive_email import (
    archive_email as _archive_email,
    archive_email_async as _archive_email_async,
)
from ..models.archive_email_response import ArchiveEmailResponse
from .mark_email_reador_unread import (
    mark_email_reador_unread as _mark_email_reador_unread,
    mark_email_reador_unread_async as _mark_email_reador_unread_async,
)
from ..models.mark_email_reador_unread_request import MarkEmailReadorUnreadRequest
from ..models.mark_email_reador_unread_response import MarkEmailReadorUnreadResponse
from .turn_on_automatic_replies import (
    turn_on_automatic_replies as _turn_on_automatic_replies,
    turn_on_automatic_replies_async as _turn_on_automatic_replies_async,
)
from ..models.turn_on_automatic_replies_request import TurnOnAutomaticRepliesRequest
from ..models.turn_on_automatic_replies_response import TurnOnAutomaticRepliesResponse
from .turn_off_automatic_replies import (
    turn_off_automatic_replies as _turn_off_automatic_replies,
    turn_off_automatic_replies_async as _turn_off_automatic_replies_async,
)
from ..models.turn_off_automatic_replies_request import TurnOffAutomaticRepliesRequest
from ..models.turn_off_automatic_replies_response import TurnOffAutomaticRepliesResponse
from .curated_calendar_event import (
    list_calendar_events as _list_calendar_events,
    list_calendar_events_async as _list_calendar_events_async,
)
from ..models.list_calendar_events import ListCalendarEvents
from .forward_email import (
    forward_email as _forward_email,
    forward_email_async as _forward_email_async,
)
from ..models.forward_email_request import ForwardEmailRequest
from .reply_to_email import (
    reply_to_email as _reply_to_email,
    reply_to_email_async as _reply_to_email_async,
)
from ..models.reply_to_email_request import ReplyToEmailRequest
from ..models.reply_to_email_response import ReplyToEmailResponse
from .send_mail import (
    send_email as _send_email,
    send_email_async as _send_email_async,
)
from ..models.send_email_request import SendEmailRequest
from ..models.send_email_response import SendEmailResponse
from .message import (
    delete_email as _delete_email,
    delete_email_async as _delete_email_async,
    list_email as _list_email,
    list_email_async as _list_email_async,
)
from ..models.list_email import ListEmail
from .get_newest_email import (
    get_newest_email as _get_newest_email,
    get_newest_email_async as _get_newest_email_async,
)
from ..models.get_newest_email_response import GetNewestEmailResponse
from .set_email_categories import (
    set_email_categories as _set_email_categories,
    set_email_categories_async as _set_email_categories_async,
)
from ..models.set_email_categories_request import SetEmailCategoriesRequest
from ..models.set_email_categories_response import SetEmailCategoriesResponse
from .download_attachment import (
    download_attachment as _download_attachment,
    download_attachment_async as _download_attachment_async,
)
from .respondto_event_invitation import (
    respondto_event_invitation as _respondto_event_invitation,
    respondto_event_invitation_async as _respondto_event_invitation_async,
)
from ..models.respondto_event_invitation_request import RespondtoEventInvitationRequest
from ..models.respondto_event_invitation_response import (
    RespondtoEventInvitationResponse,
)
from .move_email import (
    move_email as _move_email,
    move_email_async as _move_email_async,
)
from ..models.move_email_request import MoveEmailRequest
from ..models.move_email_response import MoveEmailResponse
from .mail_folder import (
    get_email_folders as _get_email_folders,
    get_email_folders_async as _get_email_folders_async,
)
from ..models.get_email_folders import GetEmailFolders
from .calendar import (
    create_calendar_event as _create_calendar_event,
    create_calendar_event_async as _create_calendar_event_async,
    update_calendar_event as _update_calendar_event,
    update_calendar_event_async as _update_calendar_event_async,
)
from ..models.create_calendar_event_request import CreateCalendarEventRequest
from ..models.create_calendar_event_response import CreateCalendarEventResponse
from ..models.update_calendar_event_request import UpdateCalendarEventRequest
from ..models.update_calendar_event_response import UpdateCalendarEventResponse

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

    def download_email(
        self,
        *,
        id: str,
        id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list[Any]]]:
        return _download_email(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    async def download_email_async(
        self,
        *,
        id: str,
        id_lookup: Any,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list[Any]]]:
        return await _download_email_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    def get_calendar_list(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        id: Optional[str] = None,
        id_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page: Optional[str] = None,
        page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCalendarList"]]]:
        return _get_calendar_list(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            id=id,
            id_lookup=id_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page=page,
            page_lookup=page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    async def get_calendar_list_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        id: Optional[str] = None,
        id_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page: Optional[str] = None,
        page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCalendarList"]]]:
        return await _get_calendar_list_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            id=id,
            id_lookup=id_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page=page,
            page_lookup=page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    def get_calendars(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCalendars"]]]:
        return _get_calendars(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    async def get_calendars_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["GetCalendars"]]]:
        return await _get_calendars_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    def forward_event(
        self,
        *,
        body: ForwardEventRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _forward_event(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    async def forward_event_async(
        self,
        *,
        body: ForwardEventRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _forward_event_async(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    def archive_email(
        self,
        *,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[ArchiveEmailResponse, DefaultError]]:
        return _archive_email(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    async def archive_email_async(
        self,
        *,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[ArchiveEmailResponse, DefaultError]]:
        return await _archive_email_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
        )

    def mark_email_reador_unread(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: MarkEmailReadorUnreadRequest,
    ) -> Optional[Union[DefaultError, MarkEmailReadorUnreadResponse]]:
        return _mark_email_reador_unread(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
        )

    async def mark_email_reador_unread_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: MarkEmailReadorUnreadRequest,
    ) -> Optional[Union[DefaultError, MarkEmailReadorUnreadResponse]]:
        return await _mark_email_reador_unread_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
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

    def list_calendar_events(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListCalendarEvents"]]]:
        return _list_calendar_events(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    async def list_calendar_events_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListCalendarEvents"]]]:
        return await _list_calendar_events_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
        )

    def forward_email(
        self,
        *,
        body: ForwardEmailRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _forward_email(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    async def forward_email_async(
        self,
        *,
        body: ForwardEmailRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _forward_email_async(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    def reply_to_email(
        self,
        *,
        body: ReplyToEmailRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, ReplyToEmailResponse]]:
        return _reply_to_email(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    async def reply_to_email_async(
        self,
        *,
        body: ReplyToEmailRequest,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[DefaultError, ReplyToEmailResponse]]:
        return await _reply_to_email_async(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
        )

    def send_email(
        self,
        *,
        body: SendEmailRequest,
    ) -> Optional[Union[DefaultError, SendEmailResponse]]:
        return _send_email(
            client=self.client,
            body=body,
        )

    async def send_email_async(
        self,
        *,
        body: SendEmailRequest,
    ) -> Optional[Union[DefaultError, SendEmailResponse]]:
        return await _send_email_async(
            client=self.client,
            body=body,
        )

    def delete_email(
        self,
        id: str,
        id_lookup: Any,
        *,
        permanently_delete: Optional[bool] = False,
        permanently_delete_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _delete_email(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            permanently_delete=permanently_delete,
            permanently_delete_lookup=permanently_delete_lookup,
        )

    async def delete_email_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        permanently_delete: Optional[bool] = False,
        permanently_delete_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _delete_email_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            permanently_delete=permanently_delete,
            permanently_delete_lookup=permanently_delete_lookup,
        )

    def list_email(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order_by: Optional[str] = None,
        order_by_lookup: Any,
        page: Optional[str] = None,
        page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        parent_folder_id: Optional[str] = None,
        parent_folder_id_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListEmail"]]]:
        return _list_email(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order_by=order_by,
            order_by_lookup=order_by_lookup,
            page=page,
            page_lookup=page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            parent_folder_id=parent_folder_id,
            parent_folder_id_lookup=parent_folder_id_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    async def list_email_async(
        self,
        *,
        fields: Optional[str] = None,
        fields_lookup: Any,
        next_page: Optional[str] = None,
        next_page_lookup: Any,
        order_by: Optional[str] = None,
        order_by_lookup: Any,
        page: Optional[str] = None,
        page_lookup: Any,
        page_size: Optional[int] = None,
        page_size_lookup: Any,
        parent_folder_id: Optional[str] = None,
        parent_folder_id_lookup: Any,
        where: Optional[str] = None,
        where_lookup: Any,
    ) -> Optional[Union[DefaultError, list["ListEmail"]]]:
        return await _list_email_async(
            client=self.client,
            fields=fields,
            fields_lookup=fields_lookup,
            next_page=next_page,
            next_page_lookup=next_page_lookup,
            order_by=order_by,
            order_by_lookup=order_by_lookup,
            page=page,
            page_lookup=page_lookup,
            page_size=page_size,
            page_size_lookup=page_size_lookup,
            parent_folder_id=parent_folder_id,
            parent_folder_id_lookup=parent_folder_id_lookup,
            where=where,
            where_lookup=where_lookup,
        )

    def get_newest_email(
        self,
        *,
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
        return _get_newest_email(
            client=self.client,
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

    async def get_newest_email_async(
        self,
        *,
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
        return await _get_newest_email_async(
            client=self.client,
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

    def set_email_categories(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: SetEmailCategoriesRequest,
    ) -> Optional[Union[DefaultError, SetEmailCategoriesResponse]]:
        return _set_email_categories(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
        )

    async def set_email_categories_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: SetEmailCategoriesRequest,
    ) -> Optional[Union[DefaultError, SetEmailCategoriesResponse]]:
        return await _set_email_categories_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
        )

    def download_attachment(
        self,
        *,
        file_name: str,
        file_name_lookup: Any,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return _download_attachment(
            client=self.client,
            file_name=file_name,
            file_name_lookup=file_name_lookup,
            id=id,
            id_lookup=id_lookup,
        )

    async def download_attachment_async(
        self,
        *,
        file_name: str,
        file_name_lookup: Any,
        id: str,
        id_lookup: Any,
    ) -> Optional[Union[Any, DefaultError]]:
        return await _download_attachment_async(
            client=self.client,
            file_name=file_name,
            file_name_lookup=file_name_lookup,
            id=id,
            id_lookup=id_lookup,
        )

    def respondto_event_invitation(
        self,
        *,
        body: RespondtoEventInvitationRequest,
        id: str,
        id_lookup: Any,
        response: str = "accept",
        response_lookup: Any,
    ) -> Optional[Union[DefaultError, RespondtoEventInvitationResponse]]:
        return _respondto_event_invitation(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
            response=response,
            response_lookup=response_lookup,
        )

    async def respondto_event_invitation_async(
        self,
        *,
        body: RespondtoEventInvitationRequest,
        id: str,
        id_lookup: Any,
        response: str = "accept",
        response_lookup: Any,
    ) -> Optional[Union[DefaultError, RespondtoEventInvitationResponse]]:
        return await _respondto_event_invitation_async(
            client=self.client,
            body=body,
            id=id,
            id_lookup=id_lookup,
            response=response,
            response_lookup=response_lookup,
        )

    def move_email(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: MoveEmailRequest,
    ) -> Optional[Union[DefaultError, MoveEmailResponse]]:
        return _move_email(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
        )

    async def move_email_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: MoveEmailRequest,
    ) -> Optional[Union[DefaultError, MoveEmailResponse]]:
        return await _move_email_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
        )

    def get_email_folders(
        self,
        *,
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
        return _get_email_folders(
            client=self.client,
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

    async def get_email_folders_async(
        self,
        *,
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
        return await _get_email_folders_async(
            client=self.client,
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

    def create_calendar_event(
        self,
        *,
        body: CreateCalendarEventRequest,
    ) -> Optional[Union[CreateCalendarEventResponse, DefaultError]]:
        return _create_calendar_event(
            client=self.client,
            body=body,
        )

    async def create_calendar_event_async(
        self,
        *,
        body: CreateCalendarEventRequest,
    ) -> Optional[Union[CreateCalendarEventResponse, DefaultError]]:
        return await _create_calendar_event_async(
            client=self.client,
            body=body,
        )

    def update_calendar_event(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: UpdateCalendarEventRequest,
    ) -> Optional[Union[DefaultError, UpdateCalendarEventResponse]]:
        return _update_calendar_event(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
        )

    async def update_calendar_event_async(
        self,
        id: str,
        id_lookup: Any,
        *,
        body: UpdateCalendarEventRequest,
    ) -> Optional[Union[DefaultError, UpdateCalendarEventResponse]]:
        return await _update_calendar_event_async(
            client=self.client,
            id=id,
            id_lookup=id_lookup,
            body=body,
        )
