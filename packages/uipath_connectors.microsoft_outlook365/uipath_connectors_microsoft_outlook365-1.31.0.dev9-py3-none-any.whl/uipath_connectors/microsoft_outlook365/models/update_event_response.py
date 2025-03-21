from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_event_response_change_attachments import (
    UpdateEventResponseChangeAttachments,
)
from ..models.update_event_response_importance import UpdateEventResponseImportance
from ..models.update_event_response_show_as import UpdateEventResponseShowAs


class UpdateEventResponse(BaseModel):
    """
    Attributes:
        change_attachments (Optional[UpdateEventResponseChangeAttachments]): Update the attachment with one of the
                provided option
        importance (Optional[UpdateEventResponseImportance]): The importance of the event.
        is_all_day (Optional[bool]): Specifies if the event lasts the entire day. Example: True.
        show_as (Optional[UpdateEventResponseShowAs]): Event status displayed in calendar
        timezone (Optional[str]): The timezone in which the event is scheduled.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    change_attachments: Optional["UpdateEventResponseChangeAttachments"] = Field(
        alias="changeAttachments", default=None
    )
    importance: Optional["UpdateEventResponseImportance"] = Field(
        alias="importance", default=None
    )
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=None)
    show_as: Optional["UpdateEventResponseShowAs"] = Field(alias="showAs", default=None)
    timezone: Optional[str] = Field(alias="timezone", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateEventResponse"], src_dict: Dict[str, Any]):
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
