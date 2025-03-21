from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.turn_off_automatic_replies_request_automatic_replies_setting import (
    TurnOffAutomaticRepliesRequestAutomaticRepliesSetting,
)


class TurnOffAutomaticRepliesRequest(BaseModel):
    """
    Attributes:
        automatic_replies_setting (Optional[TurnOffAutomaticRepliesRequestAutomaticRepliesSetting]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    automatic_replies_setting: Optional[
        "TurnOffAutomaticRepliesRequestAutomaticRepliesSetting"
    ] = Field(alias="automaticRepliesSetting", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["TurnOffAutomaticRepliesRequest"], src_dict: Dict[str, Any]
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
