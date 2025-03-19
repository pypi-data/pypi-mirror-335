from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_calendar_events_importance import ListCalendarEventsImportance
from ..models.list_calendar_events_sensitivity import ListCalendarEventsSensitivity
from ..models.list_calendar_events_show_as import ListCalendarEventsShowAs
from ..models.list_calendar_events_attendees_array_item_ref import (
    ListCalendarEventsAttendeesArrayItemRef,
)
from ..models.list_calendar_events_categories_array_item_ref import (
    ListCalendarEventsCategoriesArrayItemRef,
)
from ..models.list_calendar_events_attachments_array_item_ref import (
    ListCalendarEventsAttachmentsArrayItemRef,
)


class ListCalendarEvents(BaseModel):
    """
    Attributes:
        all_day (Optional[bool]):
        attachments (Optional[list['ListCalendarEventsAttachmentsArrayItemRef']]):
        attendees (Optional[list['ListCalendarEventsAttendeesArrayItemRef']]):
        calendar_id (Optional[str]):
        calendar_name (Optional[str]):
        categories (Optional[list['ListCalendarEventsCategoriesArrayItemRef']]):
        description (Optional[str]):
        has_attachments (Optional[bool]):
        id (Optional[str]):
        importance (Optional[ListCalendarEventsImportance]):
        location (Optional[str]):
        sensitivity (Optional[ListCalendarEventsSensitivity]):
        show_as (Optional[ListCalendarEventsShowAs]):
        title (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    all_day: Optional[bool] = Field(alias="AllDay", default=None)
    attachments: Optional[list["ListCalendarEventsAttachmentsArrayItemRef"]] = Field(
        alias="Attachments", default=None
    )
    attendees: Optional[list["ListCalendarEventsAttendeesArrayItemRef"]] = Field(
        alias="Attendees", default=None
    )
    calendar_id: Optional[str] = Field(alias="CalendarID", default=None)
    calendar_name: Optional[str] = Field(alias="CalendarName", default=None)
    categories: Optional[list["ListCalendarEventsCategoriesArrayItemRef"]] = Field(
        alias="Categories", default=None
    )
    description: Optional[str] = Field(alias="Description", default=None)
    has_attachments: Optional[bool] = Field(alias="HasAttachments", default=None)
    id: Optional[str] = Field(alias="ID", default=None)
    importance: Optional[ListCalendarEventsImportance] = Field(
        alias="Importance", default=None
    )
    location: Optional[str] = Field(alias="Location", default=None)
    sensitivity: Optional[ListCalendarEventsSensitivity] = Field(
        alias="Sensitivity", default=None
    )
    show_as: Optional[ListCalendarEventsShowAs] = Field(alias="ShowAs", default=None)
    title: Optional[str] = Field(alias="Title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListCalendarEvents"], src_dict: Dict[str, Any]):
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
