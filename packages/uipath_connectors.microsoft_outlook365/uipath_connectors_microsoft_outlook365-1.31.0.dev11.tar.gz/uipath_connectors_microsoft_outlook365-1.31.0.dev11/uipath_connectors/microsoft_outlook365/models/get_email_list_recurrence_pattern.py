from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetEmailListRecurrencePattern(BaseModel):
    """
    Attributes:
        day_of_month (Optional[int]): Specifies the day of the month for recurring events.
        days_of_week (Optional[list[str]]):
        first_day_of_week (Optional[str]): Defines the first day of the week for recurring events in the calendar.
                Example: sunday.
        index (Optional[str]): Defines the index of the recurrence pattern for the event. Example: first.
        interval (Optional[int]): Defines the interval between occurrences in a recurrence pattern. Example: 1.0.
        month (Optional[int]): Identifies the month in which the recurrence pattern occurs.
        type_ (Optional[str]): Defines the type of recurrence pattern for the event. Example: daily.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    day_of_month: Optional[int] = Field(alias="dayOfMonth", default=None)
    days_of_week: Optional[list[str]] = Field(alias="daysOfWeek", default=None)
    first_day_of_week: Optional[str] = Field(alias="firstDayOfWeek", default=None)
    index: Optional[str] = Field(alias="index", default=None)
    interval: Optional[int] = Field(alias="interval", default=None)
    month: Optional[int] = Field(alias="month", default=None)
    type_: Optional[str] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEmailListRecurrencePattern"], src_dict: Dict[str, Any]):
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
