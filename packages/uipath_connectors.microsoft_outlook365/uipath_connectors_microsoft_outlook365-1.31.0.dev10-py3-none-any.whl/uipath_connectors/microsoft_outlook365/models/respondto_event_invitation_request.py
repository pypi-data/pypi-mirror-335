from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class RespondtoEventInvitationRequest(BaseModel):
    """
    Attributes:
        comment (Optional[str]): Add a comment to your response for the event invitation. Example: sample comment.
        end_date_time (Optional[datetime.datetime]): The new date and time for the start of the event.  If left blank,
                the existing value will not be updated.
        send_response (Optional[bool]): Notify organizer of the response status Default: False.
        start_date_time (Optional[datetime.datetime]): The new date and time for the start of the event.  If left blank,
                the existing value will not be updated.
        timezone (Optional[str]): The new timezone for the event. If left blank, the existing value will not be updated.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    comment: Optional[str] = Field(alias="comment", default=None)
    end_date_time: Optional[datetime.datetime] = Field(
        alias="endDateTime", default=None
    )
    send_response: Optional[bool] = Field(alias="sendResponse", default=False)
    start_date_time: Optional[datetime.datetime] = Field(
        alias="startDateTime", default=None
    )
    timezone: Optional[str] = Field(alias="timezone", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["RespondtoEventInvitationRequest"], src_dict: Dict[str, Any]
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
