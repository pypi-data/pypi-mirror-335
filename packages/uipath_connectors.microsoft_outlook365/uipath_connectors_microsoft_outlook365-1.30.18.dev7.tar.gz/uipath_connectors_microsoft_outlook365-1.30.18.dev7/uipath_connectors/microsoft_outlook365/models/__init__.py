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
from .create_calendar_event_request import CreateCalendarEventRequest
from .create_calendar_event_request_body import CreateCalendarEventRequestBody
from .create_calendar_event_request_end import CreateCalendarEventRequestEnd
from .create_calendar_event_request_event_sensitivity_level import (
    CreateCalendarEventRequestEventSensitivityLevel,
)
from .create_calendar_event_request_importance import (
    CreateCalendarEventRequestImportance,
)
from .create_calendar_event_request_location import CreateCalendarEventRequestLocation
from .create_calendar_event_request_show_as_status import (
    CreateCalendarEventRequestShowAsStatus,
)
from .create_calendar_event_request_start import CreateCalendarEventRequestStart
from .create_calendar_event_response import CreateCalendarEventResponse
from .create_calendar_event_response_attendees_array_item_ref import (
    CreateCalendarEventResponseAttendeesArrayItemRef,
)
from .create_calendar_event_response_attendees_email_address import (
    CreateCalendarEventResponseAttendeesEmailAddress,
)
from .create_calendar_event_response_attendees_status import (
    CreateCalendarEventResponseAttendeesStatus,
)
from .create_calendar_event_response_event_type import (
    CreateCalendarEventResponseEventType,
)
from .create_calendar_event_response_location import CreateCalendarEventResponseLocation
from .create_calendar_event_response_locations_array_item_ref import (
    CreateCalendarEventResponseLocationsArrayItemRef,
)
from .create_calendar_event_response_online_meeting import (
    CreateCalendarEventResponseOnlineMeeting,
)
from .create_calendar_event_response_organizer import (
    CreateCalendarEventResponseOrganizer,
)
from .create_calendar_event_response_organizer_email_address import (
    CreateCalendarEventResponseOrganizerEmailAddress,
)
from .create_calendar_event_response_response_status import (
    CreateCalendarEventResponseResponseStatus,
)
from .default_error import DefaultError
from .forward_email_request import ForwardEmailRequest
from .forward_email_request_recipient_details import ForwardEmailRequestRecipientDetails
from .forward_event_request import ForwardEventRequest
from .forward_event_request_recipient_details import ForwardEventRequestRecipientDetails
from .get_calendar_list import GetCalendarList
from .get_calendar_list_type import GetCalendarListType
from .get_calendars import GetCalendars
from .get_calendars_owner import GetCalendarsOwner
from .get_email_folders import GetEmailFolders
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
from .list_calendar_events import ListCalendarEvents
from .list_calendar_events_attachments_array_item_ref import (
    ListCalendarEventsAttachmentsArrayItemRef,
)
from .list_calendar_events_attendees_array_item_ref import (
    ListCalendarEventsAttendeesArrayItemRef,
)
from .list_calendar_events_attendees_array_item_ref_attendee_response import (
    ListCalendarEventsAttendeesArrayItemRefAttendeeResponse,
)
from .list_calendar_events_attendees_array_item_ref_attendee_type import (
    ListCalendarEventsAttendeesArrayItemRefAttendeeType,
)
from .list_calendar_events_categories_array_item_ref import (
    ListCalendarEventsCategoriesArrayItemRef,
)
from .list_calendar_events_importance import ListCalendarEventsImportance
from .list_calendar_events_sensitivity import ListCalendarEventsSensitivity
from .list_calendar_events_show_as import ListCalendarEventsShowAs
from .list_email import ListEmail
from .list_email_bcc_recipients_array_item_ref import ListEmailBccRecipientsArrayItemRef
from .list_email_bcc_recipients_email_address import ListEmailBccRecipientsEmailAddress
from .list_email_body import ListEmailBody
from .list_email_cc_recipients_array_item_ref import ListEmailCcRecipientsArrayItemRef
from .list_email_cc_recipients_email_address import ListEmailCcRecipientsEmailAddress
from .list_email_end_date_time import ListEmailEndDateTime
from .list_email_flag import ListEmailFlag
from .list_email_from import ListEmailFrom
from .list_email_from_email_address import ListEmailFromEmailAddress
from .list_email_importance import ListEmailImportance
from .list_email_inference_classification import ListEmailInferenceClassification
from .list_email_location import ListEmailLocation
from .list_email_previous_end_date_time import ListEmailPreviousEndDateTime
from .list_email_previous_location import ListEmailPreviousLocation
from .list_email_previous_start_date_time import ListEmailPreviousStartDateTime
from .list_email_recurrence import ListEmailRecurrence
from .list_email_recurrence_pattern import ListEmailRecurrencePattern
from .list_email_recurrence_range import ListEmailRecurrenceRange
from .list_email_reply_to_array_item_ref import ListEmailReplyToArrayItemRef
from .list_email_reply_to_email_address import ListEmailReplyToEmailAddress
from .list_email_sender import ListEmailSender
from .list_email_sender_email_address import ListEmailSenderEmailAddress
from .list_email_start_date_time import ListEmailStartDateTime
from .list_email_to_recipients_array_item_ref import ListEmailToRecipientsArrayItemRef
from .list_email_to_recipients_email_address import ListEmailToRecipientsEmailAddress
from .mark_email_reador_unread_request import MarkEmailReadorUnreadRequest
from .mark_email_reador_unread_request_mark_as import MarkEmailReadorUnreadRequestMarkAs
from .mark_email_reador_unread_response import MarkEmailReadorUnreadResponse
from .mark_email_reador_unread_response_body import MarkEmailReadorUnreadResponseBody
from .mark_email_reador_unread_response_flag import MarkEmailReadorUnreadResponseFlag
from .mark_email_reador_unread_response_from import MarkEmailReadorUnreadResponseFrom
from .mark_email_reador_unread_response_from_email_address import (
    MarkEmailReadorUnreadResponseFromEmailAddress,
)
from .mark_email_reador_unread_response_mark_as import (
    MarkEmailReadorUnreadResponseMarkAs,
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
from .reply_to_email_request import ReplyToEmailRequest
from .reply_to_email_request_message import ReplyToEmailRequestMessage
from .reply_to_email_request_message_body import ReplyToEmailRequestMessageBody
from .reply_to_email_request_message_email_classification import (
    ReplyToEmailRequestMessageEmailClassification,
)
from .reply_to_email_request_message_importance import (
    ReplyToEmailRequestMessageImportance,
)
from .reply_to_email_response import ReplyToEmailResponse
from .reply_to_email_response_message import ReplyToEmailResponseMessage
from .reply_to_email_response_message_email_classification import (
    ReplyToEmailResponseMessageEmailClassification,
)
from .reply_to_email_response_message_importance import (
    ReplyToEmailResponseMessageImportance,
)
from .respondto_event_invitation_request import RespondtoEventInvitationRequest
from .respondto_event_invitation_response import RespondtoEventInvitationResponse
from .send_email_request import SendEmailRequest
from .send_email_request_message import SendEmailRequestMessage
from .send_email_request_message_body import SendEmailRequestMessageBody
from .send_email_request_message_email_classification import (
    SendEmailRequestMessageEmailClassification,
)
from .send_email_request_message_importance import SendEmailRequestMessageImportance
from .send_email_response import SendEmailResponse
from .send_email_response_internet_message_headers_array_item_ref import (
    SendEmailResponseInternetMessageHeadersArrayItemRef,
)
from .send_email_response_message import SendEmailResponseMessage
from .send_email_response_message_cc_recipients_array_item_ref import (
    SendEmailResponseMessageCcRecipientsArrayItemRef,
)
from .send_email_response_message_cc_recipients_email_address import (
    SendEmailResponseMessageCcRecipientsEmailAddress,
)
from .send_email_response_message_email_classification import (
    SendEmailResponseMessageEmailClassification,
)
from .send_email_response_message_importance import SendEmailResponseMessageImportance
from .send_email_response_message_to_recipients_array_item_ref import (
    SendEmailResponseMessageToRecipientsArrayItemRef,
)
from .send_email_response_message_to_recipients_email_address import (
    SendEmailResponseMessageToRecipientsEmailAddress,
)
from .set_email_categories_request import SetEmailCategoriesRequest
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
from .turn_on_automatic_replies_request_automatic_replies_setting_send_replies_outside_user_organization import (
    TurnOnAutomaticRepliesRequestAutomaticRepliesSettingSendRepliesOutsideUserOrganization,
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
from .turn_on_automatic_replies_response_automatic_replies_setting_send_replies_outside_user_organization import (
    TurnOnAutomaticRepliesResponseAutomaticRepliesSettingSendRepliesOutsideUserOrganization,
)
from .update_calendar_event_request import UpdateCalendarEventRequest
from .update_calendar_event_request_end import UpdateCalendarEventRequestEnd
from .update_calendar_event_request_event_sensitivity_level import (
    UpdateCalendarEventRequestEventSensitivityLevel,
)
from .update_calendar_event_request_location import UpdateCalendarEventRequestLocation
from .update_calendar_event_request_recurrence import (
    UpdateCalendarEventRequestRecurrence,
)
from .update_calendar_event_request_recurrence_pattern import (
    UpdateCalendarEventRequestRecurrencePattern,
)
from .update_calendar_event_request_recurrence_range import (
    UpdateCalendarEventRequestRecurrenceRange,
)
from .update_calendar_event_request_response_status import (
    UpdateCalendarEventRequestResponseStatus,
)
from .update_calendar_event_request_show_as_status import (
    UpdateCalendarEventRequestShowAsStatus,
)
from .update_calendar_event_request_start import UpdateCalendarEventRequestStart
from .update_calendar_event_response import UpdateCalendarEventResponse
from .update_calendar_event_response_attendees_array_item_ref import (
    UpdateCalendarEventResponseAttendeesArrayItemRef,
)
from .update_calendar_event_response_attendees_email_address import (
    UpdateCalendarEventResponseAttendeesEmailAddress,
)
from .update_calendar_event_response_attendees_status import (
    UpdateCalendarEventResponseAttendeesStatus,
)
from .update_calendar_event_response_body import UpdateCalendarEventResponseBody
from .update_calendar_event_response_end import UpdateCalendarEventResponseEnd
from .update_calendar_event_response_event_sensitivity_level import (
    UpdateCalendarEventResponseEventSensitivityLevel,
)
from .update_calendar_event_response_event_type import (
    UpdateCalendarEventResponseEventType,
)
from .update_calendar_event_response_importance import (
    UpdateCalendarEventResponseImportance,
)
from .update_calendar_event_response_location import UpdateCalendarEventResponseLocation
from .update_calendar_event_response_locations_array_item_ref import (
    UpdateCalendarEventResponseLocationsArrayItemRef,
)
from .update_calendar_event_response_online_meeting import (
    UpdateCalendarEventResponseOnlineMeeting,
)
from .update_calendar_event_response_organizer import (
    UpdateCalendarEventResponseOrganizer,
)
from .update_calendar_event_response_organizer_email_address import (
    UpdateCalendarEventResponseOrganizerEmailAddress,
)
from .update_calendar_event_response_recurrence import (
    UpdateCalendarEventResponseRecurrence,
)
from .update_calendar_event_response_recurrence_pattern import (
    UpdateCalendarEventResponseRecurrencePattern,
)
from .update_calendar_event_response_recurrence_range import (
    UpdateCalendarEventResponseRecurrenceRange,
)
from .update_calendar_event_response_response_status import (
    UpdateCalendarEventResponseResponseStatus,
)
from .update_calendar_event_response_show_as_status import (
    UpdateCalendarEventResponseShowAsStatus,
)
from .update_calendar_event_response_start import UpdateCalendarEventResponseStart

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
    "CreateCalendarEventRequest",
    "CreateCalendarEventRequestBody",
    "CreateCalendarEventRequestEnd",
    "CreateCalendarEventRequestEventSensitivityLevel",
    "CreateCalendarEventRequestImportance",
    "CreateCalendarEventRequestLocation",
    "CreateCalendarEventRequestShowAsStatus",
    "CreateCalendarEventRequestStart",
    "CreateCalendarEventResponse",
    "CreateCalendarEventResponseAttendeesArrayItemRef",
    "CreateCalendarEventResponseAttendeesEmailAddress",
    "CreateCalendarEventResponseAttendeesStatus",
    "CreateCalendarEventResponseEventType",
    "CreateCalendarEventResponseLocation",
    "CreateCalendarEventResponseLocationsArrayItemRef",
    "CreateCalendarEventResponseOnlineMeeting",
    "CreateCalendarEventResponseOrganizer",
    "CreateCalendarEventResponseOrganizerEmailAddress",
    "CreateCalendarEventResponseResponseStatus",
    "DefaultError",
    "ForwardEmailRequest",
    "ForwardEmailRequestRecipientDetails",
    "ForwardEventRequest",
    "ForwardEventRequestRecipientDetails",
    "GetCalendarList",
    "GetCalendarListType",
    "GetCalendars",
    "GetCalendarsOwner",
    "GetEmailFolders",
    "GetNewestEmailResponse",
    "GetNewestEmailResponseBody",
    "GetNewestEmailResponseFlag",
    "GetNewestEmailResponseFrom",
    "GetNewestEmailResponseFromEmailAddress",
    "GetNewestEmailResponseSender",
    "GetNewestEmailResponseSenderEmailAddress",
    "GetNewestEmailResponseToRecipientsArrayItemRef",
    "GetNewestEmailResponseToRecipientsEmailAddress",
    "ListCalendarEvents",
    "ListCalendarEventsAttachmentsArrayItemRef",
    "ListCalendarEventsAttendeesArrayItemRef",
    "ListCalendarEventsAttendeesArrayItemRefAttendeeResponse",
    "ListCalendarEventsAttendeesArrayItemRefAttendeeType",
    "ListCalendarEventsCategoriesArrayItemRef",
    "ListCalendarEventsImportance",
    "ListCalendarEventsSensitivity",
    "ListCalendarEventsShowAs",
    "ListEmail",
    "ListEmailBccRecipientsArrayItemRef",
    "ListEmailBccRecipientsEmailAddress",
    "ListEmailBody",
    "ListEmailCcRecipientsArrayItemRef",
    "ListEmailCcRecipientsEmailAddress",
    "ListEmailEndDateTime",
    "ListEmailFlag",
    "ListEmailFrom",
    "ListEmailFromEmailAddress",
    "ListEmailImportance",
    "ListEmailInferenceClassification",
    "ListEmailLocation",
    "ListEmailPreviousEndDateTime",
    "ListEmailPreviousLocation",
    "ListEmailPreviousStartDateTime",
    "ListEmailRecurrence",
    "ListEmailRecurrencePattern",
    "ListEmailRecurrenceRange",
    "ListEmailReplyToArrayItemRef",
    "ListEmailReplyToEmailAddress",
    "ListEmailSender",
    "ListEmailSenderEmailAddress",
    "ListEmailStartDateTime",
    "ListEmailToRecipientsArrayItemRef",
    "ListEmailToRecipientsEmailAddress",
    "MarkEmailReadorUnreadRequest",
    "MarkEmailReadorUnreadRequestMarkAs",
    "MarkEmailReadorUnreadResponse",
    "MarkEmailReadorUnreadResponseBody",
    "MarkEmailReadorUnreadResponseFlag",
    "MarkEmailReadorUnreadResponseFrom",
    "MarkEmailReadorUnreadResponseFromEmailAddress",
    "MarkEmailReadorUnreadResponseMarkAs",
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
    "ReplyToEmailRequest",
    "ReplyToEmailRequestMessage",
    "ReplyToEmailRequestMessageBody",
    "ReplyToEmailRequestMessageEmailClassification",
    "ReplyToEmailRequestMessageImportance",
    "ReplyToEmailResponse",
    "ReplyToEmailResponseMessage",
    "ReplyToEmailResponseMessageEmailClassification",
    "ReplyToEmailResponseMessageImportance",
    "RespondtoEventInvitationRequest",
    "RespondtoEventInvitationResponse",
    "SendEmailRequest",
    "SendEmailRequestMessage",
    "SendEmailRequestMessageBody",
    "SendEmailRequestMessageEmailClassification",
    "SendEmailRequestMessageImportance",
    "SendEmailResponse",
    "SendEmailResponseInternetMessageHeadersArrayItemRef",
    "SendEmailResponseMessage",
    "SendEmailResponseMessageCcRecipientsArrayItemRef",
    "SendEmailResponseMessageCcRecipientsEmailAddress",
    "SendEmailResponseMessageEmailClassification",
    "SendEmailResponseMessageImportance",
    "SendEmailResponseMessageToRecipientsArrayItemRef",
    "SendEmailResponseMessageToRecipientsEmailAddress",
    "SetEmailCategoriesRequest",
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
    "TurnOnAutomaticRepliesRequestAutomaticRepliesSettingSendRepliesOutsideUserOrganization",
    "TurnOnAutomaticRepliesResponse",
    "TurnOnAutomaticRepliesResponseAutomaticRepliesSetting",
    "TurnOnAutomaticRepliesResponseAutomaticRepliesSettingScheduledEndDateTime",
    "TurnOnAutomaticRepliesResponseAutomaticRepliesSettingScheduledStartDateTime",
    "TurnOnAutomaticRepliesResponseAutomaticRepliesSettingSendRepliesOutsideUserOrganization",
    "UpdateCalendarEventRequest",
    "UpdateCalendarEventRequestEnd",
    "UpdateCalendarEventRequestEventSensitivityLevel",
    "UpdateCalendarEventRequestLocation",
    "UpdateCalendarEventRequestRecurrence",
    "UpdateCalendarEventRequestRecurrencePattern",
    "UpdateCalendarEventRequestRecurrenceRange",
    "UpdateCalendarEventRequestResponseStatus",
    "UpdateCalendarEventRequestShowAsStatus",
    "UpdateCalendarEventRequestStart",
    "UpdateCalendarEventResponse",
    "UpdateCalendarEventResponseAttendeesArrayItemRef",
    "UpdateCalendarEventResponseAttendeesEmailAddress",
    "UpdateCalendarEventResponseAttendeesStatus",
    "UpdateCalendarEventResponseBody",
    "UpdateCalendarEventResponseEnd",
    "UpdateCalendarEventResponseEventSensitivityLevel",
    "UpdateCalendarEventResponseEventType",
    "UpdateCalendarEventResponseImportance",
    "UpdateCalendarEventResponseLocation",
    "UpdateCalendarEventResponseLocationsArrayItemRef",
    "UpdateCalendarEventResponseOnlineMeeting",
    "UpdateCalendarEventResponseOrganizer",
    "UpdateCalendarEventResponseOrganizerEmailAddress",
    "UpdateCalendarEventResponseRecurrence",
    "UpdateCalendarEventResponseRecurrencePattern",
    "UpdateCalendarEventResponseRecurrenceRange",
    "UpdateCalendarEventResponseResponseStatus",
    "UpdateCalendarEventResponseShowAsStatus",
    "UpdateCalendarEventResponseStart",
)
