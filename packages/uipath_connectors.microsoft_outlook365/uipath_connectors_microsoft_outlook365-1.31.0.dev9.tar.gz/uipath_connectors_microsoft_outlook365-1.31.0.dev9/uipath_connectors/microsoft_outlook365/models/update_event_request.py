from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_event_request_body import UpdateEventRequestBody
from ..models.update_event_request_change_categories import (
    UpdateEventRequestChangeCategories,
)
from ..models.update_event_request_change_optional_attendees import (
    UpdateEventRequestChangeOptionalAttendees,
)
from ..models.update_event_request_change_required_attendees import (
    UpdateEventRequestChangeRequiredAttendees,
)
from ..models.update_event_request_change_resource_attendees import (
    UpdateEventRequestChangeResourceAttendees,
)
from ..models.update_event_request_end import UpdateEventRequestEnd
from ..models.update_event_request_importance import UpdateEventRequestImportance
from ..models.update_event_request_location import UpdateEventRequestLocation
from ..models.update_event_request_show_as import UpdateEventRequestShowAs
from ..models.update_event_request_start import UpdateEventRequestStart


class UpdateEventRequest(BaseModel):
    """
    Attributes:
        add_categories (Optional[list[str]]):
        add_optional_attendees (Optional[str]): Indicates attendee(s) to be added
        add_required_attendees (Optional[str]): Indicates attendee(s) to be added
        add_resource_attendees (Optional[str]): Indicates attendee(s) to be added
        body (Optional[UpdateEventRequestBody]):
        categories (Optional[list[str]]):
        change_categories (Optional[UpdateEventRequestChangeCategories]): Updates the categories list with one of the
                given option
        change_optional_attendees (Optional[UpdateEventRequestChangeOptionalAttendees]): Update the optional attendees
                via one of the given options
        change_required_attendees (Optional[UpdateEventRequestChangeRequiredAttendees]): Update the required attendees
                via one of the given options
        change_resource_attendees (Optional[UpdateEventRequestChangeResourceAttendees]): Update the resource attendees
                via one of the given options
        end (Optional[UpdateEventRequestEnd]):
        importance (Optional[UpdateEventRequestImportance]): The importance of the event.
        is_all_day (Optional[bool]): Specifies if the event lasts the entire day. Example: True.
        is_online_meeting (Optional[bool]): Specifies if the meeting should be online (only Microsoft Teams is
                supported).
        location (Optional[UpdateEventRequestLocation]):
        optional_attendees (Optional[str]): Indicate the attendee(s) or the attendees list that should replaced
        remove_categories (Optional[list[str]]):
        remove_optional_attendees (Optional[str]): Indicates attendee(s) to be removed
        remove_required_attendees (Optional[str]): Indicates attendee(s) to be removed
        remove_resource_attendees (Optional[str]): Indicates attendee(s) to be removed
        required_attendees (Optional[str]): Indicate the attendee(s) or the attendees list that should replaced
        resource_attendees (Optional[str]): Indicate the attendee(s) or the attendees list that should replaced
        sensitivity (Optional[str]): Defines the privacy level of the event, such as public or private.
        show_as (Optional[UpdateEventRequestShowAs]): Event status displayed in calendar
        start (Optional[UpdateEventRequestStart]):
        subject (Optional[str]): The new name of the event. If left blank, the existing value will not be updated.
        timezone (Optional[str]): The timezone in which the event is scheduled.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    add_categories: Optional[list[str]] = Field(alias="addCategories", default=None)
    add_optional_attendees: Optional[str] = Field(
        alias="addOptionalAttendees", default=None
    )
    add_required_attendees: Optional[str] = Field(
        alias="addRequiredAttendees", default=None
    )
    add_resource_attendees: Optional[str] = Field(
        alias="addResourceAttendees", default=None
    )
    body: Optional["UpdateEventRequestBody"] = Field(alias="body", default=None)
    categories: Optional[list[str]] = Field(alias="categories", default=None)
    change_categories: Optional["UpdateEventRequestChangeCategories"] = Field(
        alias="changeCategories", default=None
    )
    change_optional_attendees: Optional["UpdateEventRequestChangeOptionalAttendees"] = (
        Field(alias="changeOptionalAttendees", default=None)
    )
    change_required_attendees: Optional["UpdateEventRequestChangeRequiredAttendees"] = (
        Field(alias="changeRequiredAttendees", default=None)
    )
    change_resource_attendees: Optional["UpdateEventRequestChangeResourceAttendees"] = (
        Field(alias="changeResourceAttendees", default=None)
    )
    end: Optional["UpdateEventRequestEnd"] = Field(alias="end", default=None)
    importance: Optional["UpdateEventRequestImportance"] = Field(
        alias="importance", default=None
    )
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=None)
    is_online_meeting: Optional[bool] = Field(alias="isOnlineMeeting", default=None)
    location: Optional["UpdateEventRequestLocation"] = Field(
        alias="location", default=None
    )
    optional_attendees: Optional[str] = Field(alias="optionalAttendees", default=None)
    remove_categories: Optional[list[str]] = Field(
        alias="removeCategories", default=None
    )
    remove_optional_attendees: Optional[str] = Field(
        alias="removeOptionalAttendees", default=None
    )
    remove_required_attendees: Optional[str] = Field(
        alias="removeRequiredAttendees", default=None
    )
    remove_resource_attendees: Optional[str] = Field(
        alias="removeResourceAttendees", default=None
    )
    required_attendees: Optional[str] = Field(alias="requiredAttendees", default=None)
    resource_attendees: Optional[str] = Field(alias="resourceAttendees", default=None)
    sensitivity: Optional[str] = Field(alias="sensitivity", default=None)
    show_as: Optional["UpdateEventRequestShowAs"] = Field(alias="showAs", default=None)
    start: Optional["UpdateEventRequestStart"] = Field(alias="start", default=None)
    subject: Optional[str] = Field(alias="subject", default=None)
    timezone: Optional[str] = Field(alias="timezone", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateEventRequest"], src_dict: Dict[str, Any]):
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
