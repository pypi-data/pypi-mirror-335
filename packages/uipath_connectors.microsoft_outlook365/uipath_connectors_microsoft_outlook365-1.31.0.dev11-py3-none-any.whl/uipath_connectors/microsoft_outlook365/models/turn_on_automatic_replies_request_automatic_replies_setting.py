from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.turn_on_automatic_replies_request_automatic_replies_setting_scheduled_end_date_time import (
    TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledEndDateTime,
)
from ..models.turn_on_automatic_replies_request_automatic_replies_setting_scheduled_start_date_time import (
    TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledStartDateTime,
)


class TurnOnAutomaticRepliesRequestAutomaticRepliesSetting(BaseModel):
    """
    Attributes:
        internal_reply_message (str): The message sent automatically to internal senders. Example: I am currently out of
                the office. Please reach out to [Backup Person] for urgent matters..
        external_audience (Optional[bool]): Specifies who receives automatic replies outside the organization. Default:
                False. Example: none.
        external_reply_message (Optional[str]): The message sent automatically to external recipients. Example: Thank
                you for reaching out. I am currently out of the office and will respond as soon as possible..
        scheduled_end_date_time (Optional[TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledEndDateTime]):
        scheduled_start_date_time
                (Optional[TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledStartDateTime]):
        status (Optional[str]): Indicates whether automatic replies are enabled or disabled. Default: 'scheduled'.
                Example: scheduled.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    internal_reply_message: str = Field(alias="internalReplyMessage")
    external_audience: Optional[bool] = Field(alias="externalAudience", default=False)
    external_reply_message: Optional[str] = Field(
        alias="externalReplyMessage", default=None
    )
    scheduled_end_date_time: Optional[
        "TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledEndDateTime"
    ] = Field(alias="scheduledEndDateTime", default=None)
    scheduled_start_date_time: Optional[
        "TurnOnAutomaticRepliesRequestAutomaticRepliesSettingScheduledStartDateTime"
    ] = Field(alias="scheduledStartDateTime", default=None)
    status: Optional[str] = Field(alias="status", default="scheduled")

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["TurnOnAutomaticRepliesRequestAutomaticRepliesSetting"],
        src_dict: Dict[str, Any],
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
