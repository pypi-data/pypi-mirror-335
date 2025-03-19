from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_email_request_message_email_classification import (
    SendEmailRequestMessageEmailClassification,
)
from ..models.send_email_request_message_importance import (
    SendEmailRequestMessageImportance,
)
from ..models.send_email_request_message_body import SendEmailRequestMessageBody


class SendEmailRequestMessage(BaseModel):
    """
    Attributes:
        bcc_recipients (Optional[str]): Comma separated lists the email addresses of recipients who are blind copied on
                the email.
        body (Optional[SendEmailRequestMessageBody]):
        cc_recipients (Optional[str]): Comma separated lists the email addresses of recipients who are copied on the
                email.
        importance (Optional[SendEmailRequestMessageImportance]): Indicates the priority level of the email message.
                Example: high.
        inference_classification (Optional[SendEmailRequestMessageEmailClassification]): The classification of the email
                based on inferred importance.
        internet_message_headers (Optional[str]): Message internal headers
        subject (Optional[str]): The subject line of the email message.
        to_recipients (Optional[str]): Comma separated list of recipients to whom the email is addressed.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bcc_recipients: Optional[str] = Field(alias="bccRecipients", default=None)
    body: Optional["SendEmailRequestMessageBody"] = Field(alias="body", default=None)
    cc_recipients: Optional[str] = Field(alias="ccRecipients", default=None)
    importance: Optional[SendEmailRequestMessageImportance] = Field(
        alias="importance", default=None
    )
    inference_classification: Optional[SendEmailRequestMessageEmailClassification] = (
        Field(alias="inferenceClassification", default=None)
    )
    internet_message_headers: Optional[str] = Field(
        alias="internetMessageHeaders", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[str] = Field(alias="toRecipients", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendEmailRequestMessage"], src_dict: Dict[str, Any]):
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
