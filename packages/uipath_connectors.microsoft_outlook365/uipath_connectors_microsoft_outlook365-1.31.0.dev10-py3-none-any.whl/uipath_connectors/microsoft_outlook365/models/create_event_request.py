from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_event_request_body import CreateEventRequestBody
from ..models.create_event_request_end import CreateEventRequestEnd
from ..models.create_event_request_importance import CreateEventRequestImportance
from ..models.create_event_request_location import CreateEventRequestLocation
from ..models.create_event_request_sensitivity import CreateEventRequestSensitivity
from ..models.create_event_request_show_as import CreateEventRequestShowAs
from ..models.create_event_request_start import CreateEventRequestStart


class CreateEventRequest(BaseModel):
    """
    Attributes:
        start (Optional[CreateEventRequestStart]):
        subject (str): Title → e.g. Event title
        timezone (str): Chose or type a value
        allow_new_time_proposals (Optional[bool]): Indicates if attendees can propose new times for the event. Default:
                True. Example: True.
        body (Optional[CreateEventRequestBody]):
        categories (Optional[list[str]]):
        end (Optional[CreateEventRequestEnd]):
        hide_attendees (Optional[bool]): Indicates if attendees are hidden from the calendar event. Default: True.
                Example: True.
        importance (Optional[CreateEventRequestImportance]): Defines the priority level of the calendar event.
        is_all_day (Optional[bool]): Indicates if the event lasts the entire day. Default: False.
        is_online_meeting (Optional[bool]): Indicates if the meeting is set as an online meeting. Should only be marked
                as true for Teams meeting. Default: True. Example: True.
        location (Optional[CreateEventRequestLocation]):
        optional_attendees (Optional[str]): Comma separated list of optional attendees.
        required_attendees (Optional[str]): Comma separated list of required attendees.
        resource_attendees (Optional[str]): Comma separated list of resources, like rooms or equipment, invited to the
                event.
        sensitivity (Optional[CreateEventRequestSensitivity]): Indicates the privacy level of the calendar event.
        show_as (Optional[CreateEventRequestShowAs]): Indicates how the event appears on the calendar, like busy or
                free.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    subject: str = Field(alias="subject")
    timezone: str = Field(alias="timezone")
    start: Optional["CreateEventRequestStart"] = Field(alias="start", default=None)
    allow_new_time_proposals: Optional[bool] = Field(
        alias="allowNewTimeProposals", default=True
    )
    body: Optional["CreateEventRequestBody"] = Field(alias="body", default=None)
    categories: Optional[list[str]] = Field(alias="categories", default=None)
    end: Optional["CreateEventRequestEnd"] = Field(alias="end", default=None)
    hide_attendees: Optional[bool] = Field(alias="hideAttendees", default=True)
    importance: Optional["CreateEventRequestImportance"] = Field(
        alias="importance", default=None
    )
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=False)
    is_online_meeting: Optional[bool] = Field(alias="isOnlineMeeting", default=True)
    location: Optional["CreateEventRequestLocation"] = Field(
        alias="location", default=None
    )
    optional_attendees: Optional[str] = Field(alias="optionalAttendees", default=None)
    required_attendees: Optional[str] = Field(alias="requiredAttendees", default=None)
    resource_attendees: Optional[str] = Field(alias="resourceAttendees", default=None)
    sensitivity: Optional["CreateEventRequestSensitivity"] = Field(
        alias="sensitivity", default=None
    )
    show_as: Optional["CreateEventRequestShowAs"] = Field(alias="showAs", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateEventRequest"], src_dict: Dict[str, Any]):
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
