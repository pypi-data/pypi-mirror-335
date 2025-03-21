from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_event_by_id_response_attendees_array_item_ref import (
    GetEventByIDResponseAttendeesArrayItemRef,
)
from ..models.get_event_by_id_response_body import GetEventByIDResponseBody
from ..models.get_event_by_id_response_end import GetEventByIDResponseEnd
from ..models.get_event_by_id_response_importance import GetEventByIDResponseImportance
from ..models.get_event_by_id_response_location import GetEventByIDResponseLocation
from ..models.get_event_by_id_response_locations_array_item_ref import (
    GetEventByIDResponseLocationsArrayItemRef,
)
from ..models.get_event_by_id_response_online_meeting import (
    GetEventByIDResponseOnlineMeeting,
)
from ..models.get_event_by_id_response_organizer import GetEventByIDResponseOrganizer
from ..models.get_event_by_id_response_recurrence import GetEventByIDResponseRecurrence
from ..models.get_event_by_id_response_response_status import (
    GetEventByIDResponseResponseStatus,
)
from ..models.get_event_by_id_response_sensitivity import (
    GetEventByIDResponseSensitivity,
)
from ..models.get_event_by_id_response_show_as import GetEventByIDResponseShowAs
from ..models.get_event_by_id_response_start import GetEventByIDResponseStart
from ..models.get_event_by_id_response_type import GetEventByIDResponseType
import datetime


class GetEventByIDResponse(BaseModel):
    """
    Attributes:
        allow_new_time_proposals (Optional[bool]): Indicates if attendees can propose new times for the event. Default:
                True. Example: True.
        attendees (Optional[list['GetEventByIDResponseAttendeesArrayItemRef']]):
        body (Optional[GetEventByIDResponseBody]):
        body_preview (Optional[str]): A short preview of the event's description or content.
        change_key (Optional[str]): A unique identifier for tracking changes to the event.
        created_date_time (Optional[datetime.datetime]): The date and time when the calendar event was created.
        end (Optional[GetEventByIDResponseEnd]):
        has_attachments (Optional[bool]): Indicates whether the calendar event includes attachments.
        hide_attendees (Optional[bool]): Indicates if attendees are hidden from the calendar event. Default: True.
                Example: True.
        i_cal_u_id (Optional[str]): A unique identifier for the calendar event in iCalendar format.
        id (Optional[str]): A unique identifier for the calendar event.
        importance (Optional[GetEventByIDResponseImportance]): Defines the priority level of the calendar event.
        is_all_day (Optional[bool]): Indicates if the event lasts the entire day. Default: False.
        is_cancelled (Optional[bool]): Shows whether the event has been cancelled.
        is_draft (Optional[bool]): Indicates if the calendar event is saved as a draft.
        is_online_meeting (Optional[bool]): Indicates if the meeting is set as an online meeting. Should only be marked
                as true for Teams meeting. Default: True. Example: True.
        is_organizer (Optional[bool]): Indicates whether the user is the organizer of the event.
        is_reminder_on (Optional[bool]): Indicates if a reminder is set for the event.
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the calendar entry was last
                updated.
        location (Optional[GetEventByIDResponseLocation]):
        locations (Optional[list['GetEventByIDResponseLocationsArrayItemRef']]):
        online_meeting (Optional[GetEventByIDResponseOnlineMeeting]):
        online_meeting_provider (Optional[str]): The service used for hosting the online meeting.
        online_meeting_url (Optional[str]): The web link to join the online meeting associated with the event.
        organizer (Optional[GetEventByIDResponseOrganizer]):
        original_end_time_zone (Optional[str]): The time zone in which the event originally ends.
        original_start_time_zone (Optional[str]): The time zone in which the event was originally scheduled.
        recurrence (Optional[GetEventByIDResponseRecurrence]):
        reminder_minutes_before_start (Optional[int]): The number of minutes before the event to send a reminder.
        response_requested (Optional[bool]): Indicates if a response is requested from attendees.
        response_status (Optional[GetEventByIDResponseResponseStatus]):
        sensitivity (Optional[GetEventByIDResponseSensitivity]): Indicates the privacy level of the calendar event.
        show_as (Optional[GetEventByIDResponseShowAs]): Indicates how the event appears on the calendar, like busy or
                free.
        start (Optional[GetEventByIDResponseStart]):
        subject (Optional[str]): Title → e.g. Event title
        transaction_id (Optional[str]): A unique identifier for tracking the calendar action transaction. Example:
                7E163156-7762-4BEB-A1C6-729EA81755A7.
        type_ (Optional[GetEventByIDResponseType]): Specifies the type of calendar event or action.
        web_link (Optional[str]): A URL link to access the calendar event online.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_new_time_proposals: Optional[bool] = Field(
        alias="allowNewTimeProposals", default=True
    )
    attendees: Optional[list["GetEventByIDResponseAttendeesArrayItemRef"]] = Field(
        alias="attendees", default=None
    )
    body: Optional["GetEventByIDResponseBody"] = Field(alias="body", default=None)
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    end: Optional["GetEventByIDResponseEnd"] = Field(alias="end", default=None)
    has_attachments: Optional[bool] = Field(alias="hasAttachments", default=None)
    hide_attendees: Optional[bool] = Field(alias="hideAttendees", default=True)
    i_cal_u_id: Optional[str] = Field(alias="iCalUId", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional["GetEventByIDResponseImportance"] = Field(
        alias="importance", default=None
    )
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=False)
    is_cancelled: Optional[bool] = Field(alias="isCancelled", default=None)
    is_draft: Optional[bool] = Field(alias="isDraft", default=None)
    is_online_meeting: Optional[bool] = Field(alias="isOnlineMeeting", default=True)
    is_organizer: Optional[bool] = Field(alias="isOrganizer", default=None)
    is_reminder_on: Optional[bool] = Field(alias="isReminderOn", default=None)
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    location: Optional["GetEventByIDResponseLocation"] = Field(
        alias="location", default=None
    )
    locations: Optional[list["GetEventByIDResponseLocationsArrayItemRef"]] = Field(
        alias="locations", default=None
    )
    online_meeting: Optional["GetEventByIDResponseOnlineMeeting"] = Field(
        alias="onlineMeeting", default=None
    )
    online_meeting_provider: Optional[str] = Field(
        alias="onlineMeetingProvider", default=None
    )
    online_meeting_url: Optional[str] = Field(alias="onlineMeetingUrl", default=None)
    organizer: Optional["GetEventByIDResponseOrganizer"] = Field(
        alias="organizer", default=None
    )
    original_end_time_zone: Optional[str] = Field(
        alias="originalEndTimeZone", default=None
    )
    original_start_time_zone: Optional[str] = Field(
        alias="originalStartTimeZone", default=None
    )
    recurrence: Optional["GetEventByIDResponseRecurrence"] = Field(
        alias="recurrence", default=None
    )
    reminder_minutes_before_start: Optional[int] = Field(
        alias="reminderMinutesBeforeStart", default=None
    )
    response_requested: Optional[bool] = Field(alias="responseRequested", default=None)
    response_status: Optional["GetEventByIDResponseResponseStatus"] = Field(
        alias="responseStatus", default=None
    )
    sensitivity: Optional["GetEventByIDResponseSensitivity"] = Field(
        alias="sensitivity", default=None
    )
    show_as: Optional["GetEventByIDResponseShowAs"] = Field(
        alias="showAs", default=None
    )
    start: Optional["GetEventByIDResponseStart"] = Field(alias="start", default=None)
    subject: Optional[str] = Field(alias="subject", default=None)
    transaction_id: Optional[str] = Field(alias="transactionId", default=None)
    type_: Optional["GetEventByIDResponseType"] = Field(alias="type", default=None)
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEventByIDResponse"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
