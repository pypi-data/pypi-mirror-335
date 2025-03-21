from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_calendars_owner import GetCalendarsOwner


class GetCalendars(BaseModel):
    """
    Attributes:
        allowed_online_meeting_providers (Optional[list[str]]):
        can_edit (Optional[bool]):
        can_share (Optional[bool]):
        can_view_private_items (Optional[bool]):
        change_key (Optional[str]):
        color (Optional[str]):
        default_online_meeting_provider (Optional[str]):
        hex_color (Optional[str]):
        id (Optional[str]):
        is_default_calendar (Optional[bool]):
        is_removable (Optional[bool]):
        is_tallying_responses (Optional[bool]):
        name (Optional[str]):
        odata_id (Optional[str]):
        owner (Optional[GetCalendarsOwner]):
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
    odata_id: Optional[str] = Field(alias="odataId", default=None)
    owner: Optional["GetCalendarsOwner"] = Field(alias="owner", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetCalendars"], src_dict: Dict[str, Any]):
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
