from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_calendar_event_request_event_sensitivity_level import (
    CreateCalendarEventRequestEventSensitivityLevel,
)
from ..models.create_calendar_event_request_importance import (
    CreateCalendarEventRequestImportance,
)
from ..models.create_calendar_event_request_show_as_status import (
    CreateCalendarEventRequestShowAsStatus,
)
from ..models.create_calendar_event_request_location import (
    CreateCalendarEventRequestLocation,
)
from ..models.create_calendar_event_request_body import CreateCalendarEventRequestBody
from ..models.create_calendar_event_request_start import CreateCalendarEventRequestStart
from ..models.create_calendar_event_request_end import CreateCalendarEventRequestEnd


class CreateCalendarEventRequest(BaseModel):
    """
    Attributes:
        allow_new_time_proposals (Optional[bool]): Indicates if attendees can propose new times for the event. Example:
                True.
        body (Optional[CreateCalendarEventRequestBody]):
        end (Optional[CreateCalendarEventRequestEnd]):
        hide_attendees (Optional[bool]): Indicates if attendees are hidden from the calendar event. Example: True.
        importance (Optional[CreateCalendarEventRequestImportance]): Defines the priority level of the calendar event.
        is_all_day (Optional[bool]): Indicates if the event lasts the entire day.
        is_online_meeting (Optional[bool]): Indicates if the meeting is set as an online meeting. Should only be marked
                as true for Teams meeting. Example: True.
        location (Optional[CreateCalendarEventRequestLocation]):
        optional_attendees (Optional[str]): Comma separated list of optional attendees.
        required_attendees (Optional[str]): Comma separated list of required attendees.
        resource_attendees (Optional[str]): Comma separated list of resources, like rooms or equipment, invited to the
                event.
        sensitivity (Optional[CreateCalendarEventRequestEventSensitivityLevel]): Indicates the privacy level of the
                calendar event.
        show_as (Optional[CreateCalendarEventRequestShowAsStatus]): Indicates how the event appears on the calendar,
                like busy or free.
        start (Optional[CreateCalendarEventRequestStart]):
        subject (Optional[str]): The title or subject of the calendar event.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allow_new_time_proposals: Optional[bool] = Field(
        alias="allowNewTimeProposals", default=None
    )
    body: Optional["CreateCalendarEventRequestBody"] = Field(alias="body", default=None)
    end: Optional["CreateCalendarEventRequestEnd"] = Field(alias="end", default=None)
    hide_attendees: Optional[bool] = Field(alias="hideAttendees", default=None)
    importance: Optional[CreateCalendarEventRequestImportance] = Field(
        alias="importance", default=None
    )
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=None)
    is_online_meeting: Optional[bool] = Field(alias="isOnlineMeeting", default=None)
    location: Optional["CreateCalendarEventRequestLocation"] = Field(
        alias="location", default=None
    )
    optional_attendees: Optional[str] = Field(alias="optionalAttendees", default=None)
    required_attendees: Optional[str] = Field(alias="requiredAttendees", default=None)
    resource_attendees: Optional[str] = Field(alias="resourceAttendees", default=None)
    sensitivity: Optional[CreateCalendarEventRequestEventSensitivityLevel] = Field(
        alias="sensitivity", default=None
    )
    show_as: Optional[CreateCalendarEventRequestShowAsStatus] = Field(
        alias="showAs", default=None
    )
    start: Optional["CreateCalendarEventRequestStart"] = Field(
        alias="start", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateCalendarEventRequest"], src_dict: Dict[str, Any]):
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
