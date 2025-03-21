from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetEventByIDResponseLocationsArrayItemRef(BaseModel):
    """
    Attributes:
        display_name (Optional[str]): The name displayed for each location in the calendar.
        location_type (Optional[str]): Defines the type of location for the event, such as physical or virtual.
        unique_id (Optional[str]): A unique identifier for each location associated with the event.
        unique_id_type (Optional[str]): Specifies the type of unique ID for each location.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    display_name: Optional[str] = Field(alias="displayName", default=None)
    location_type: Optional[str] = Field(alias="locationType", default=None)
    unique_id: Optional[str] = Field(alias="uniqueId", default=None)
    unique_id_type: Optional[str] = Field(alias="uniqueIdType", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetEventByIDResponseLocationsArrayItemRef"], src_dict: Dict[str, Any]
    ):
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
