"""Contains all the data models used in inputs/outputs"""

from .archive_email_response import ArchiveEmailResponse
from .archive_email_response_body import ArchiveEmailResponseBody
from .archive_email_response_flag import ArchiveEmailResponseFlag
from .archive_email_response_from import ArchiveEmailResponseFrom
from .archive_email_response_from_email_address import (
    ArchiveEmailResponseFromEmailAddress,
)
from .archive_email_response_sender import ArchiveEmailResponseSender
from .archive_email_response_sender_email_address import (
    ArchiveEmailResponseSenderEmailAddress,
)
from .archive_email_response_to_recipients_array_item_ref import (
    ArchiveEmailResponseToRecipientsArrayItemRef,
)
from .archive_email_response_to_recipients_email_address import (
    ArchiveEmailResponseToRecipientsEmailAddress,
)
from .create_event_body import CreateEventBody
from .create_event_request import CreateEventRequest
from .create_event_request_body import CreateEventRequestBody
from .create_event_request_end import CreateEventRequestEnd
from .create_event_request_importance import CreateEventRequestImportance
from .create_event_request_location import CreateEventRequestLocation
from .create_event_request_sensitivity import CreateEventRequestSensitivity
from .create_event_request_show_as import CreateEventRequestShowAs
from .create_event_request_start import CreateEventRequestStart
from .create_event_response import CreateEventResponse
from .create_event_response_attendees_array_item_ref import (
    CreateEventResponseAttendeesArrayItemRef,
)
from .create_event_response_attendees_email_address import (
    CreateEventResponseAttendeesEmailAddress,
)
from .create_event_response_attendees_status import CreateEventResponseAttendeesStatus
from .create_event_response_location import CreateEventResponseLocation
from .create_event_response_locations_array_item_ref import (
    CreateEventResponseLocationsArrayItemRef,
)
from .create_event_response_online_meeting import CreateEventResponseOnlineMeeting
from .create_event_response_organizer import CreateEventResponseOrganizer
from .create_event_response_organizer_email_address import (
    CreateEventResponseOrganizerEmailAddress,
)
from .create_event_response_response_status import CreateEventResponseResponseStatus
from .create_event_response_type import CreateEventResponseType
from .default_error import DefaultError
from .download_attachment_response import DownloadAttachmentResponse
from .download_email import DownloadEmail
from .forward_email_body import ForwardEmailBody
from .forward_email_request import ForwardEmailRequest
from .forward_email_request_message import ForwardEmailRequestMessage
from .forward_event_request import ForwardEventRequest
from .get_calendars import GetCalendars
from .get_calendars_owner import GetCalendarsOwner
from .get_email_folders import GetEmailFolders
from .get_email_list import GetEmailList
from .get_email_list_body import GetEmailListBody
from .get_email_list_end_date_time import GetEmailListEndDateTime
from .get_email_list_flag import GetEmailListFlag
from .get_email_list_from import GetEmailListFrom
from .get_email_list_from_email_address import GetEmailListFromEmailAddress
from .get_email_list_location import GetEmailListLocation
from .get_email_list_odata import GetEmailListOdata
from .get_email_list_previous_end_date_time import GetEmailListPreviousEndDateTime
from .get_email_list_previous_start_date_time import GetEmailListPreviousStartDateTime
from .get_email_list_recurrence import GetEmailListRecurrence
from .get_email_list_recurrence_pattern import GetEmailListRecurrencePattern
from .get_email_list_recurrence_range import GetEmailListRecurrenceRange
from .get_email_list_sender import GetEmailListSender
from .get_email_list_sender_email_address import GetEmailListSenderEmailAddress
from .get_email_list_start_date_time import GetEmailListStartDateTime
from .get_email_list_to_recipients_array_item_ref import (
    GetEmailListToRecipientsArrayItemRef,
)
from .get_email_list_to_recipients_email_address import (
    GetEmailListToRecipientsEmailAddress,
)
from .get_event_by_id_response import GetEventByIDResponse
from .get_event_by_id_response_attendees_array_item_ref import (
    GetEventByIDResponseAttendeesArrayItemRef,
)
from .get_event_by_id_response_attendees_email_address import (
    GetEventByIDResponseAttendeesEmailAddress,
)
from .get_event_by_id_response_attendees_status import (
    GetEventByIDResponseAttendeesStatus,
)
from .get_event_by_id_response_body import GetEventByIDResponseBody
from .get_event_by_id_response_end import GetEventByIDResponseEnd
from .get_event_by_id_response_importance import GetEventByIDResponseImportance
from .get_event_by_id_response_location import GetEventByIDResponseLocation
from .get_event_by_id_response_locations_array_item_ref import (
    GetEventByIDResponseLocationsArrayItemRef,
)
from .get_event_by_id_response_online_meeting import GetEventByIDResponseOnlineMeeting
from .get_event_by_id_response_organizer import GetEventByIDResponseOrganizer
from .get_event_by_id_response_organizer_email_address import (
    GetEventByIDResponseOrganizerEmailAddress,
)
from .get_event_by_id_response_recurrence import GetEventByIDResponseRecurrence
from .get_event_by_id_response_recurrence_pattern import (
    GetEventByIDResponseRecurrencePattern,
)
from .get_event_by_id_response_recurrence_range import (
    GetEventByIDResponseRecurrenceRange,
)
from .get_event_by_id_response_response_status import GetEventByIDResponseResponseStatus
from .get_event_by_id_response_sensitivity import GetEventByIDResponseSensitivity
from .get_event_by_id_response_show_as import GetEventByIDResponseShowAs
from .get_event_by_id_response_start import GetEventByIDResponseStart
from .get_event_by_id_response_type import GetEventByIDResponseType
from .get_event_list import GetEventList
from .get_event_list_attendees_array_item_ref import GetEventListAttendeesArrayItemRef
from .get_event_list_attendees_email_address import GetEventListAttendeesEmailAddress
from .get_event_list_attendees_status import GetEventListAttendeesStatus
from .get_event_list_body import GetEventListBody
from .get_event_list_calendar import GetEventListCalendar
from .get_event_list_calendar_owner import GetEventListCalendarOwner
from .get_event_list_calendarodata import GetEventListCalendarodata
from .get_event_list_end import GetEventListEnd
from .get_event_list_location import GetEventListLocation
from .get_event_list_odata import GetEventListOdata
from .get_event_list_organizer import GetEventListOrganizer
from .get_event_list_organizer_email_address import GetEventListOrganizerEmailAddress
from .get_event_list_response_status import GetEventListResponseStatus
from .get_event_list_start import GetEventListStart
from .get_newest_email_response import GetNewestEmailResponse
from .get_newest_email_response_body import GetNewestEmailResponseBody
from .get_newest_email_response_flag import GetNewestEmailResponseFlag
from .get_newest_email_response_from import GetNewestEmailResponseFrom
from .get_newest_email_response_from_email_address import (
    GetNewestEmailResponseFromEmailAddress,
)
from .get_newest_email_response_sender import GetNewestEmailResponseSender
from .get_newest_email_response_sender_email_address import (
    GetNewestEmailResponseSenderEmailAddress,
)
from .get_newest_email_response_to_recipients_array_item_ref import (
    GetNewestEmailResponseToRecipientsArrayItemRef,
)
from .get_newest_email_response_to_recipients_email_address import (
    GetNewestEmailResponseToRecipientsEmailAddress,
)
from .mark_email_reador_unread_request import MarkEmailReadorUnreadRequest
from .mark_email_reador_unread_request_is_read import MarkEmailReadorUnreadRequestIsRead
from .mark_email_reador_unread_response import MarkEmailReadorUnreadResponse
from .mark_email_reador_unread_response_body import MarkEmailReadorUnreadResponseBody
from .mark_email_reador_unread_response_flag import MarkEmailReadorUnreadResponseFlag
from .mark_email_reador_unread_response_from import MarkEmailReadorUnreadResponseFrom
from .mark_email_reador_unread_response_from_email_address import (
    MarkEmailReadorUnreadResponseFromEmailAddress,
)
from .mark_email_reador_unread_response_is_read import (
    MarkEmailReadorUnreadResponseIsRead,
)
from .mark_email_reador_unread_response_reply_to_array_item_ref import (
    MarkEmailReadorUnreadResponseReplyToArrayItemRef,
)
from .mark_email_reador_unread_response_reply_to_email_address import (
    MarkEmailReadorUnreadResponseReplyToEmailAddress,
)
from .mark_email_reador_unread_response_sender import (
    MarkEmailReadorUnreadResponseSender,
)
from .mark_email_reador_unread_response_sender_email_address import (
    MarkEmailReadorUnreadResponseSenderEmailAddress,
)
from .mark_email_reador_unread_response_to_recipients_array_item_ref import (
    MarkEmailReadorUnreadResponseToRecipientsArrayItemRef,
)
from .mark_email_reador_unread_response_to_recipients_email_address import (
    MarkEmailReadorUnreadResponseToRecipientsEmailAddress,
)
from .move_email_request import MoveEmailRequest
from .move_email_response import MoveEmailResponse
from .move_email_response_body import MoveEmailResponseBody
from .move_email_response_flag import MoveEmailResponseFlag
from .move_email_response_from import MoveEmailResponseFrom
from .move_email_response_from_email_address import MoveEmailResponseFromEmailAddress
from .move_email_response_sender import MoveEmailResponseSender
from .move_email_response_sender_email_address import (
    MoveEmailResponseSenderEmailAddress,
)
from .move_email_response_to_recipients_array_item_ref import (
    MoveEmailResponseToRecipientsArrayItemRef,
)
from .move_email_response_to_recipients_email_address import (
    MoveEmailResponseToRecipientsEmailAddress,
)
from .reply_to_email_body import ReplyToEmailBody
from .reply_to_email_request import ReplyToEmailRequest
from .reply_to_email_request_message import ReplyToEmailRequestMessage
from .reply_to_email_request_message_importance import (
    ReplyToEmailRequestMessageImportance,
)
from .respondto_event_invitation_request import RespondtoEventInvitationRequest
from .respondto_event_invitation_response import RespondtoEventInvitationResponse
from .send_email_body import SendEmailBody
from .send_email_request import SendEmailRequest
from .send_email_request_message import SendEmailRequestMessage
from .send_email_request_message_body import SendEmailRequestMessageBody
from .send_email_request_message_importance import SendEmailRequestMessageImportance
from .send_email_request_message_inference_classification import (
    SendEmailRequestMessageInferenceClassification,
)
from .send_email_response import SendEmailResponse
from .set_email_categories_request import SetEmailCategoriesRequest
from .set_email_categories_request_remove_categories_option import (
    SetEmailCategoriesRequestRemoveCategoriesOption,
)
from .set_email_categories_response import SetEmailCategoriesResponse
from .set_email_categories_response_body import SetEmailCategoriesResponseBody
from .set_email_categories_response_flag import SetEmailCategoriesResponseFlag
from .set_email_categories_response_from import SetEmailCategoriesResponseFrom
from .set_email_categories_response_from_email_address import (
    SetEmailCategoriesResponseFromEmailAddress,
)
from .set_email_categories_response_reply_to_array_item_ref import (
    SetEmailCategoriesResponseReplyToArrayItemRef,
)
from .set_email_categories_response_reply_to_email_address import (
    SetEmailCategoriesResponseReplyToEmailAddress,
)
from .set_email_categories_response_sender import SetEmailCategoriesResponseSender
from .set_email_categories_response_sender_email_address import (
    SetEmailCategoriesResponseSenderEmailAddress,
)
from .set_email_categories_response_to_recipients_array_item_ref import (
    SetEmailCategoriesResponseToRecipientsArrayItemRef,
)
from .set_email_categories_response_to_recipients_email_address import (
    SetEmailCategoriesResponseToRecipientsEmailAddress,
)
from .turn_off_automatic_replies_request import TurnOffAutomaticRepliesRequest
from .turn_off_automatic_replies_request_automatic_replies_setting import (
    TurnOffAutomaticRepliesRequestAutomaticRepliesSetting,
)
from .turn_off_automatic_replies_response import TurnOffAutomaticRepliesResponse
from .turn_off_automatic_replies_response_automatic_replies_setting import (
    TurnOffAutomaticRepliesResponseAutomaticRepliesSetting,
)
from .turn_off_automatic_replies_response_automatic_replies_setting_scheduled_end_date_time import (
    TurnOffAutomaticRepliesResponseAutomaticRepliesSettingScheduledEndDateTime,
)
from .turn_off_automatic_replies_response_automatic_replies_setting_scheduled_start_date_time import (
    TurnOffAutomaticRepliesResponseAutomaticRepliesSettingScheduledStartDateTime,
)
from .turn_on_automatic_replies_request import TurnOnAutomaticRepliesRequest
from .turn_on_automatic_replies_request_automatic_replies_setting import (
    TurnOnAutomaticRepliesRequestAutomaticRepliesSetting,
)
from .turn_on_automatic_replies_request_automatic_replies_setting_scheduled_end_date_time import (
    TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledEndDateTime,
)
from .turn_on_automatic_replies_request_automatic_replies_setting_scheduled_start_date_time import (
    TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledStartDateTime,
)
from .turn_on_automatic_replies_response import TurnOnAutomaticRepliesResponse
from .turn_on_automatic_replies_response_automatic_replies_setting import (
    TurnOnAutomaticRepliesResponseAutomaticRepliesSetting,
)
from .turn_on_automatic_replies_response_automatic_replies_setting_scheduled_end_date_time import (
    TurnOnAutomaticRepliesResponseAutomaticRepliesSettingScheduledEndDateTime,
)
from .turn_on_automatic_replies_response_automatic_replies_setting_scheduled_start_date_time import (
    TurnOnAutomaticRepliesResponseAutomaticRepliesSettingScheduledStartDateTime,
)
from .update_event_body import UpdateEventBody
from .update_event_request import UpdateEventRequest
from .update_event_request_body import UpdateEventRequestBody
from .update_event_request_change_categories import UpdateEventRequestChangeCategories
from .update_event_request_change_optional_attendees import (
    UpdateEventRequestChangeOptionalAttendees,
)
from .update_event_request_change_required_attendees import (
    UpdateEventRequestChangeRequiredAttendees,
)
from .update_event_request_change_resource_attendees import (
    UpdateEventRequestChangeResourceAttendees,
)
from .update_event_request_end import UpdateEventRequestEnd
from .update_event_request_importance import UpdateEventRequestImportance
from .update_event_request_location import UpdateEventRequestLocation
from .update_event_request_show_as import UpdateEventRequestShowAs
from .update_event_request_start import UpdateEventRequestStart
from .update_event_response import UpdateEventResponse
from .update_event_response_change_attachments import (
    UpdateEventResponseChangeAttachments,
)
from .update_event_response_importance import UpdateEventResponseImportance
from .update_event_response_show_as import UpdateEventResponseShowAs

__all__ = (
    "ArchiveEmailResponse",
    "ArchiveEmailResponseBody",
    "ArchiveEmailResponseFlag",
    "ArchiveEmailResponseFrom",
    "ArchiveEmailResponseFromEmailAddress",
    "ArchiveEmailResponseSender",
    "ArchiveEmailResponseSenderEmailAddress",
    "ArchiveEmailResponseToRecipientsArrayItemRef",
    "ArchiveEmailResponseToRecipientsEmailAddress",
    "CreateEventBody",
    "CreateEventRequest",
    "CreateEventRequestBody",
    "CreateEventRequestEnd",
    "CreateEventRequestImportance",
    "CreateEventRequestLocation",
    "CreateEventRequestSensitivity",
    "CreateEventRequestShowAs",
    "CreateEventRequestStart",
    "CreateEventResponse",
    "CreateEventResponseAttendeesArrayItemRef",
    "CreateEventResponseAttendeesEmailAddress",
    "CreateEventResponseAttendeesStatus",
    "CreateEventResponseLocation",
    "CreateEventResponseLocationsArrayItemRef",
    "CreateEventResponseOnlineMeeting",
    "CreateEventResponseOrganizer",
    "CreateEventResponseOrganizerEmailAddress",
    "CreateEventResponseResponseStatus",
    "CreateEventResponseType",
    "DefaultError",
    "DownloadAttachmentResponse",
    "DownloadEmail",
    "ForwardEmailBody",
    "ForwardEmailRequest",
    "ForwardEmailRequestMessage",
    "ForwardEventRequest",
    "GetCalendars",
    "GetCalendarsOwner",
    "GetEmailFolders",
    "GetEmailList",
    "GetEmailListBody",
    "GetEmailListEndDateTime",
    "GetEmailListFlag",
    "GetEmailListFrom",
    "GetEmailListFromEmailAddress",
    "GetEmailListLocation",
    "GetEmailListOdata",
    "GetEmailListPreviousEndDateTime",
    "GetEmailListPreviousStartDateTime",
    "GetEmailListRecurrence",
    "GetEmailListRecurrencePattern",
    "GetEmailListRecurrenceRange",
    "GetEmailListSender",
    "GetEmailListSenderEmailAddress",
    "GetEmailListStartDateTime",
    "GetEmailListToRecipientsArrayItemRef",
    "GetEmailListToRecipientsEmailAddress",
    "GetEventByIDResponse",
    "GetEventByIDResponseAttendeesArrayItemRef",
    "GetEventByIDResponseAttendeesEmailAddress",
    "GetEventByIDResponseAttendeesStatus",
    "GetEventByIDResponseBody",
    "GetEventByIDResponseEnd",
    "GetEventByIDResponseImportance",
    "GetEventByIDResponseLocation",
    "GetEventByIDResponseLocationsArrayItemRef",
    "GetEventByIDResponseOnlineMeeting",
    "GetEventByIDResponseOrganizer",
    "GetEventByIDResponseOrganizerEmailAddress",
    "GetEventByIDResponseRecurrence",
    "GetEventByIDResponseRecurrencePattern",
    "GetEventByIDResponseRecurrenceRange",
    "GetEventByIDResponseResponseStatus",
    "GetEventByIDResponseSensitivity",
    "GetEventByIDResponseShowAs",
    "GetEventByIDResponseStart",
    "GetEventByIDResponseType",
    "GetEventList",
    "GetEventListAttendeesArrayItemRef",
    "GetEventListAttendeesEmailAddress",
    "GetEventListAttendeesStatus",
    "GetEventListBody",
    "GetEventListCalendar",
    "GetEventListCalendarodata",
    "GetEventListCalendarOwner",
    "GetEventListEnd",
    "GetEventListLocation",
    "GetEventListOdata",
    "GetEventListOrganizer",
    "GetEventListOrganizerEmailAddress",
    "GetEventListResponseStatus",
    "GetEventListStart",
    "GetNewestEmailResponse",
    "GetNewestEmailResponseBody",
    "GetNewestEmailResponseFlag",
    "GetNewestEmailResponseFrom",
    "GetNewestEmailResponseFromEmailAddress",
    "GetNewestEmailResponseSender",
    "GetNewestEmailResponseSenderEmailAddress",
    "GetNewestEmailResponseToRecipientsArrayItemRef",
    "GetNewestEmailResponseToRecipientsEmailAddress",
    "MarkEmailReadorUnreadRequest",
    "MarkEmailReadorUnreadRequestIsRead",
    "MarkEmailReadorUnreadResponse",
    "MarkEmailReadorUnreadResponseBody",
    "MarkEmailReadorUnreadResponseFlag",
    "MarkEmailReadorUnreadResponseFrom",
    "MarkEmailReadorUnreadResponseFromEmailAddress",
    "MarkEmailReadorUnreadResponseIsRead",
    "MarkEmailReadorUnreadResponseReplyToArrayItemRef",
    "MarkEmailReadorUnreadResponseReplyToEmailAddress",
    "MarkEmailReadorUnreadResponseSender",
    "MarkEmailReadorUnreadResponseSenderEmailAddress",
    "MarkEmailReadorUnreadResponseToRecipientsArrayItemRef",
    "MarkEmailReadorUnreadResponseToRecipientsEmailAddress",
    "MoveEmailRequest",
    "MoveEmailResponse",
    "MoveEmailResponseBody",
    "MoveEmailResponseFlag",
    "MoveEmailResponseFrom",
    "MoveEmailResponseFromEmailAddress",
    "MoveEmailResponseSender",
    "MoveEmailResponseSenderEmailAddress",
    "MoveEmailResponseToRecipientsArrayItemRef",
    "MoveEmailResponseToRecipientsEmailAddress",
    "ReplyToEmailBody",
    "ReplyToEmailRequest",
    "ReplyToEmailRequestMessage",
    "ReplyToEmailRequestMessageImportance",
    "RespondtoEventInvitationRequest",
    "RespondtoEventInvitationResponse",
    "SendEmailBody",
    "SendEmailRequest",
    "SendEmailRequestMessage",
    "SendEmailRequestMessageBody",
    "SendEmailRequestMessageImportance",
    "SendEmailRequestMessageInferenceClassification",
    "SendEmailResponse",
    "SetEmailCategoriesRequest",
    "SetEmailCategoriesRequestRemoveCategoriesOption",
    "SetEmailCategoriesResponse",
    "SetEmailCategoriesResponseBody",
    "SetEmailCategoriesResponseFlag",
    "SetEmailCategoriesResponseFrom",
    "SetEmailCategoriesResponseFromEmailAddress",
    "SetEmailCategoriesResponseReplyToArrayItemRef",
    "SetEmailCategoriesResponseReplyToEmailAddress",
    "SetEmailCategoriesResponseSender",
    "SetEmailCategoriesResponseSenderEmailAddress",
    "SetEmailCategoriesResponseToRecipientsArrayItemRef",
    "SetEmailCategoriesResponseToRecipientsEmailAddress",
    "TurnOffAutomaticRepliesRequest",
    "TurnOffAutomaticRepliesRequestAutomaticRepliesSetting",
    "TurnOffAutomaticRepliesResponse",
    "TurnOffAutomaticRepliesResponseAutomaticRepliesSetting",
    "TurnOffAutomaticRepliesResponseAutomaticRepliesSettingScheduledEndDateTime",
    "TurnOffAutomaticRepliesResponseAutomaticRepliesSettingScheduledStartDateTime",
    "TurnOnAutomaticRepliesRequest",
    "TurnOnAutomaticRepliesRequestAutomaticRepliesSetting",
    "TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledEndDateTime",
    "TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledStartDateTime",
    "TurnOnAutomaticRepliesResponse",
    "TurnOnAutomaticRepliesResponseAutomaticRepliesSetting",
    "TurnOnAutomaticRepliesResponseAutomaticRepliesSettingScheduledEndDateTime",
    "TurnOnAutomaticRepliesResponseAutomaticRepliesSettingScheduledStartDateTime",
    "UpdateEventBody",
    "UpdateEventRequest",
    "UpdateEventRequestBody",
    "UpdateEventRequestChangeCategories",
    "UpdateEventRequestChangeOptionalAttendees",
    "UpdateEventRequestChangeRequiredAttendees",
    "UpdateEventRequestChangeResourceAttendees",
    "UpdateEventRequestEnd",
    "UpdateEventRequestImportance",
    "UpdateEventRequestLocation",
    "UpdateEventRequestShowAs",
    "UpdateEventRequestStart",
    "UpdateEventResponse",
    "UpdateEventResponseChangeAttachments",
    "UpdateEventResponseImportance",
    "UpdateEventResponseShowAs",
)
