from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_event_response_attendees_array_item_ref import (
    CreateEventResponseAttendeesArrayItemRef,
)
from ..models.create_event_response_location import CreateEventResponseLocation
from ..models.create_event_response_locations_array_item_ref import (
    CreateEventResponseLocationsArrayItemRef,
)
from ..models.create_event_response_online_meeting import (
    CreateEventResponseOnlineMeeting,
)
from ..models.create_event_response_organizer import CreateEventResponseOrganizer
from ..models.create_event_response_response_status import (
    CreateEventResponseResponseStatus,
)
from ..models.create_event_response_type import CreateEventResponseType
import datetime


class CreateEventResponse(BaseModel):
    """
    Attributes:
        attendees (Optional[list['CreateEventResponseAttendeesArrayItemRef']]):
        body_preview (Optional[str]): A short preview of the event's description or content.
        change_key (Optional[str]): A unique identifier for tracking changes to the event.
        created_date_time (Optional[datetime.datetime]): The date and time when the calendar event was created.
        has_attachments (Optional[bool]): Indicates whether the calendar event includes attachments.
        i_cal_u_id (Optional[str]): A unique identifier for the calendar event in iCalendar format.
        id (Optional[str]): A unique identifier for the calendar event.
        is_cancelled (Optional[bool]): Shows whether the event has been cancelled.
        is_draft (Optional[bool]): Indicates if the calendar event is saved as a draft.
        is_organizer (Optional[bool]): Indicates whether the user is the organizer of the event.
        is_reminder_on (Optional[bool]): Indicates if a reminder is set for the event.
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the calendar entry was last
                updated.
        location (Optional[CreateEventResponseLocation]):
        locations (Optional[list['CreateEventResponseLocationsArrayItemRef']]):
        online_meeting (Optional[CreateEventResponseOnlineMeeting]):
        online_meeting_provider (Optional[str]): The service used for hosting the online meeting.
        online_meeting_url (Optional[str]): The web link to join the online meeting associated with the event.
        organizer (Optional[CreateEventResponseOrganizer]):
        original_end_time_zone (Optional[str]): The time zone in which the event originally ends.
        original_start_time_zone (Optional[str]): The time zone in which the event was originally scheduled.
        reminder_minutes_before_start (Optional[int]): The number of minutes before the event to send a reminder.
        response_requested (Optional[bool]): Indicates if a response is requested from attendees.
        response_status (Optional[CreateEventResponseResponseStatus]):
        transaction_id (Optional[str]): A unique identifier for tracking the calendar action transaction. Example:
                7E163156-7762-4BEB-A1C6-729EA81755A7.
        type_ (Optional[CreateEventResponseType]): Specifies the type of calendar event or action.
        web_link (Optional[str]): A URL link to access the calendar event online.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    attendees: Optional[list["CreateEventResponseAttendeesArrayItemRef"]] = Field(
        alias="attendees", default=None
    )
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    has_attachments: Optional[bool] = Field(alias="hasAttachments", default=None)
    i_cal_u_id: Optional[str] = Field(alias="iCalUId", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_cancelled: Optional[bool] = Field(alias="isCancelled", default=None)
    is_draft: Optional[bool] = Field(alias="isDraft", default=None)
    is_organizer: Optional[bool] = Field(alias="isOrganizer", default=None)
    is_reminder_on: Optional[bool] = Field(alias="isReminderOn", default=None)
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    location: Optional["CreateEventResponseLocation"] = Field(
        alias="location", default=None
    )
    locations: Optional[list["CreateEventResponseLocationsArrayItemRef"]] = Field(
        alias="locations", default=None
    )
    online_meeting: Optional["CreateEventResponseOnlineMeeting"] = Field(
        alias="onlineMeeting", default=None
    )
    online_meeting_provider: Optional[str] = Field(
        alias="onlineMeetingProvider", default=None
    )
    online_meeting_url: Optional[str] = Field(alias="onlineMeetingUrl", default=None)
    organizer: Optional["CreateEventResponseOrganizer"] = Field(
        alias="organizer", default=None
    )
    original_end_time_zone: Optional[str] = Field(
        alias="originalEndTimeZone", default=None
    )
    original_start_time_zone: Optional[str] = Field(
        alias="originalStartTimeZone", default=None
    )
    reminder_minutes_before_start: Optional[int] = Field(
        alias="reminderMinutesBeforeStart", default=None
    )
    response_requested: Optional[bool] = Field(alias="responseRequested", default=None)
    response_status: Optional["CreateEventResponseResponseStatus"] = Field(
        alias="responseStatus", default=None
    )
    transaction_id: Optional[str] = Field(alias="transactionId", default=None)
    type_: Optional["CreateEventResponseType"] = Field(alias="type", default=None)
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateEventResponse"], src_dict: Dict[str, Any]):
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
