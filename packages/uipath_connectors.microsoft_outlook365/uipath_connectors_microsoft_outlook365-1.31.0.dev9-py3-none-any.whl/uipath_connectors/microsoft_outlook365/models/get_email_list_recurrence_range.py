from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class GetEmailListRecurrenceRange(BaseModel):
    """
    Attributes:
        end_date (Optional[datetime.datetime]): The date when the recurrence pattern ends. Example: 2025-09-10.
        number_of_occurrences (Optional[int]): Specifies the total number of occurrences for the recurrence.
        recurrence_time_zone (Optional[str]): The time zone used for the recurrence of the event. Example:
                tzone://Microsoft/Utc.
        start_date (Optional[datetime.datetime]): The date when the recurrence pattern begins. Example: 2025-03-10.
        type_ (Optional[str]): Specifies the type of range for the recurrence pattern. Example: endDate.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    end_date: Optional[datetime.datetime] = Field(alias="endDate", default=None)
    number_of_occurrences: Optional[int] = Field(
        alias="numberOfOccurrences", default=None
    )
    recurrence_time_zone: Optional[str] = Field(
        alias="recurrenceTimeZone", default=None
    )
    start_date: Optional[datetime.datetime] = Field(alias="startDate", default=None)
    type_: Optional[str] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEmailListRecurrenceRange"], src_dict: Dict[str, Any]):
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
