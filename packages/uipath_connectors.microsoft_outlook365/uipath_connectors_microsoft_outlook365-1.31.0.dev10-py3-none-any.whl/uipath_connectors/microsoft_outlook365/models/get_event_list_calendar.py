from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_event_list_calendar_owner import GetEventListCalendarOwner


class GetEventListCalendar(BaseModel):
    """
    Attributes:
        allowed_online_meeting_providers (Optional[list[str]]):
        can_edit (Optional[bool]): Indicates if the calendar can be edited by the user. Example: True.
        can_share (Optional[bool]): Indicates if the calendar can be shared with others. Example: True.
        can_view_private_items (Optional[bool]): Indicates if the user can view private items in the calendar. Example:
                True.
        change_key (Optional[str]): A unique identifier for the current version of the calendar. Example:
                fB9lPtoEj0ughhcAqPIaCgAAAJtq0w==.
        color (Optional[str]): Predefined color assigned to the calendar. Example: auto.
        default_online_meeting_provider (Optional[str]): Specifies the default provider for online meetings in the
                calendar. Example: teamsForBusiness.
        hex_color (Optional[str]): Hexadecimal code representing the calendar's color.
        id (Optional[str]): A unique identifier for the calendar where the event is stored. Example: AAMkADJmOGNjOTYwLWM
                zOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNABGAAAAAACheKuSte_nRYh5zSjSpULXBwB8H2U_2gSPS6CGFwCo8hoKAAAAAAEGAAB8H2U_2gSPS6C
                GFwCo8hoKAAAAm-qXAAA=.
        is_default_calendar (Optional[bool]): Shows if the event belongs to the default calendar. Example: True.
        is_removable (Optional[bool]): Indicates if the calendar can be removed by the user.
        is_tallying_responses (Optional[bool]): Indicates if the calendar is counting event responses. Example: True.
        name (Optional[str]): The name of the calendar where the event is scheduled. Example: Calendar.
        owner (Optional[GetEventListCalendarOwner]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    allowed_online_meeting_providers: Optional[list[str]] = Field(
        alias="allowedOnlineMeetingProviders", default=None
    )
    can_edit: Optional[bool] = Field(alias="canEdit", default=None)
    can_share: Optional[bool] = Field(alias="canShare", default=None)
    can_view_private_items: Optional[bool] = Field(
        alias="canViewPrivateItems", default=None
    )
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    color: Optional[str] = Field(alias="color", default=None)
    default_online_meeting_provider: Optional[str] = Field(
        alias="defaultOnlineMeetingProvider", default=None
    )
    hex_color: Optional[str] = Field(alias="hexColor", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    is_default_calendar: Optional[bool] = Field(alias="isDefaultCalendar", default=None)
    is_removable: Optional[bool] = Field(alias="isRemovable", default=None)
    is_tallying_responses: Optional[bool] = Field(
        alias="isTallyingResponses", default=None
    )
    name: Optional[str] = Field(alias="name", default=None)
    owner: Optional["GetEventListCalendarOwner"] = Field(alias="owner", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEventListCalendar"], src_dict: Dict[str, Any]):
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
