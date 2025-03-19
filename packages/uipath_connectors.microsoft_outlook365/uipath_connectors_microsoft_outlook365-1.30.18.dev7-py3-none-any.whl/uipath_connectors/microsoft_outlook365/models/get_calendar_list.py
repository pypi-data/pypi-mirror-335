from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_calendar_list_type import GetCalendarListType


class GetCalendarList(BaseModel):
    """
    Attributes:
        full_name (Optional[str]):  Example: My Calendars.
        id (Optional[str]):  Example: AAMkADVmMmEzMTRmLTk4MTEtNDJkNS05ZDRkLWQ0YThiMzc0MDM4MABGAAAAAADlG0IEqKbKQpghWUIiJw
                YnBwDUm1Np7nOgR4BU0efoFfUnAAAAAAEGAADUm1Np7nOgR4BU0efoFfUnAAABM5hFAAA=.
        selectable (Optional[bool]):  Example: True.
        type_ (Optional[GetCalendarListType]):
        calendar_id (Optional[str]):  Example: AAMkADVmMmEzMTRmLTk4MTEtNDJkNS05ZDRkLWQ0YThiMzc0MDM4MABGAAAAAADlG0IEqKbKQ
                pghWUIiJwYnBwDUm1Np7nOgR4BU0efoFfUnAAAAAAEGAADUm1Np7nOgR4BU0efoFfUnAAABM5hFAAA=.
        is_folder (Optional[bool]):  Example: True.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    full_name: Optional[str] = Field(alias="FullName", default=None)
    id: Optional[str] = Field(alias="ID", default=None)
    selectable: Optional[bool] = Field(alias="Selectable", default=None)
    type_: Optional[GetCalendarListType] = Field(alias="Type", default=None)
    calendar_id: Optional[str] = Field(alias="calendarID", default=None)
    is_folder: Optional[bool] = Field(alias="isFolder", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetCalendarList"], src_dict: Dict[str, Any]):
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
