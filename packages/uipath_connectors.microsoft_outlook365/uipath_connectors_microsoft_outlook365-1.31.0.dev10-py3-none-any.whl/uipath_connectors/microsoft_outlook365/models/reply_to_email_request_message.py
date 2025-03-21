from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.reply_to_email_request_message_importance import (
    ReplyToEmailRequestMessageImportance,
)


class ReplyToEmailRequestMessage(BaseModel):
    """
    Attributes:
        bcc_recipients (Optional[str]): Comma separated list of additional hidden recipients of the email
        cc_recipients (Optional[str]): Comma separated list of additional secondary recipients of the email
        importance (Optional[ReplyToEmailRequestMessageImportance]): The importance of the mail. Example: high.
        subject (Optional[str]): The new subject of the email. If left blank the original subject is used.
        to_recipients (Optional[str]): Comma separated email address of additional primary recipients of the email
                Example: harish.reddy@uipath.com, testing@uipath.con.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bcc_recipients: Optional[str] = Field(alias="bccRecipients", default=None)
    cc_recipients: Optional[str] = Field(alias="ccRecipients", default=None)
    importance: Optional["ReplyToEmailRequestMessageImportance"] = Field(
        alias="importance", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[str] = Field(alias="toRecipients", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ReplyToEmailRequestMessage"], src_dict: Dict[str, Any]):
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
