from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_calendar_event_request_event_sensitivity_level import (
    UpdateCalendarEventRequestEventSensitivityLevel,
)
from ..models.update_calendar_event_request_show_as_status import (
    UpdateCalendarEventRequestShowAsStatus,
)
from ..models.update_calendar_event_request_end import UpdateCalendarEventRequestEnd
from ..models.update_calendar_event_request_start import UpdateCalendarEventRequestStart
from ..models.update_calendar_event_request_recurrence import (
    UpdateCalendarEventRequestRecurrence,
)
from ..models.update_calendar_event_request_response_status import (
    UpdateCalendarEventRequestResponseStatus,
)
from ..models.update_calendar_event_request_location import (
    UpdateCalendarEventRequestLocation,
)


class UpdateCalendarEventRequest(BaseModel):
    """
    Attributes:
        categories (Optional[list[str]]):
        end (Optional[UpdateCalendarEventRequestEnd]):
        hide_attendees (Optional[bool]): Indicates if attendees are hidden from the calendar event. Example: True.
        is_all_day (Optional[bool]): Indicates if the event lasts the entire day.
        is_online_meeting (Optional[bool]): Indicates if the meeting is set as an online meeting. Should only be marked
                as true for Teams meeting. Example: True.
        is_reminder_on (Optional[bool]): Indicates if a reminder is set for the event.
        location (Optional[UpdateCalendarEventRequestLocation]):
        online_meeting_provider (Optional[str]): The service used for hosting the online meeting.
        optional_attendees (Optional[str]): Comma separated list of optional attendees.
        original_end_time_zone (Optional[str]): The time zone in which the event originally ends.
        original_start_time_zone (Optional[str]): The time zone in which the event was originally scheduled.
        recurrence (Optional[UpdateCalendarEventRequestRecurrence]):
        reminder_minutes_before_start (Optional[int]): The number of minutes before the event to send a reminder.
        required_attendees (Optional[str]): Comma separated list of required attendees.
        resource_attendees (Optional[str]): Comma separated list of resources, like rooms or equipment, invited to the
                event.
        response_requested (Optional[bool]): Indicates if a response is requested from attendees.
        response_status (Optional[UpdateCalendarEventRequestResponseStatus]):
        sensitivity (Optional[UpdateCalendarEventRequestEventSensitivityLevel]): Indicates the privacy level of the
                calendar event.
        show_as (Optional[UpdateCalendarEventRequestShowAsStatus]): Indicates how the event appears on the calendar,
                like busy or free.
        start (Optional[UpdateCalendarEventRequestStart]):
        subject (Optional[str]): The title or subject of the calendar event.
        transaction_id (Optional[str]): A unique identifier for tracking the calendar action transaction. Example:
                7E163156-7762-4BEB-A1C6-729EA81755A7.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    categories: Optional[list[str]] = Field(alias="categories", default=None)
    end: Optional["UpdateCalendarEventRequestEnd"] = Field(alias="end", default=None)
    hide_attendees: Optional[bool] = Field(alias="hideAttendees", default=None)
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=None)
    is_online_meeting: Optional[bool] = Field(alias="isOnlineMeeting", default=None)
    is_reminder_on: Optional[bool] = Field(alias="isReminderOn", default=None)
    location: Optional["UpdateCalendarEventRequestLocation"] = Field(
        alias="location", default=None
    )
    online_meeting_provider: Optional[str] = Field(
        alias="onlineMeetingProvider", default=None
    )
    optional_attendees: Optional[str] = Field(alias="optionalAttendees", default=None)
    original_end_time_zone: Optional[str] = Field(
        alias="originalEndTimeZone", default=None
    )
    original_start_time_zone: Optional[str] = Field(
        alias="originalStartTimeZone", default=None
    )
    recurrence: Optional["UpdateCalendarEventRequestRecurrence"] = Field(
        alias="recurrence", default=None
    )
    reminder_minutes_before_start: Optional[int] = Field(
        alias="reminderMinutesBeforeStart", default=None
    )
    required_attendees: Optional[str] = Field(alias="requiredAttendees", default=None)
    resource_attendees: Optional[str] = Field(alias="resourceAttendees", default=None)
    response_requested: Optional[bool] = Field(alias="responseRequested", default=None)
    response_status: Optional["UpdateCalendarEventRequestResponseStatus"] = Field(
        alias="responseStatus", default=None
    )
    sensitivity: Optional[UpdateCalendarEventRequestEventSensitivityLevel] = Field(
        alias="sensitivity", default=None
    )
    show_as: Optional[UpdateCalendarEventRequestShowAsStatus] = Field(
        alias="showAs", default=None
    )
    start: Optional["UpdateCalendarEventRequestStart"] = Field(
        alias="start", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    transaction_id: Optional[str] = Field(alias="transactionId", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateCalendarEventRequest"], src_dict: Dict[str, Any]):
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
