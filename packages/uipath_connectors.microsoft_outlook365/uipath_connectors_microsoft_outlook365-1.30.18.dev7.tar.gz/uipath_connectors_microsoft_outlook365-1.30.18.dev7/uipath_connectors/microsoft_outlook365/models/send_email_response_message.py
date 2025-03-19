from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.send_email_response_message_email_classification import (
    SendEmailResponseMessageEmailClassification,
)
from ..models.send_email_response_message_importance import (
    SendEmailResponseMessageImportance,
)
from ..models.send_email_response_message_cc_recipients_array_item_ref import (
    SendEmailResponseMessageCcRecipientsArrayItemRef,
)
from ..models.send_email_response_message_to_recipients_array_item_ref import (
    SendEmailResponseMessageToRecipientsArrayItemRef,
)


class SendEmailResponseMessage(BaseModel):
    """
    Attributes:
        cc_recipients (Optional[list['SendEmailResponseMessageCcRecipientsArrayItemRef']]):
        importance (Optional[SendEmailResponseMessageImportance]): Indicates the priority level of the email message.
                Example: high.
        inference_classification (Optional[SendEmailResponseMessageEmailClassification]): The classification of the
                email based on inferred importance.
        to_recipients (Optional[list['SendEmailResponseMessageToRecipientsArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    cc_recipients: Optional[
        list["SendEmailResponseMessageCcRecipientsArrayItemRef"]
    ] = Field(alias="ccRecipients", default=None)
    importance: Optional[SendEmailResponseMessageImportance] = Field(
        alias="importance", default=None
    )
    inference_classification: Optional[SendEmailResponseMessageEmailClassification] = (
        Field(alias="inferenceClassification", default=None)
    )
    to_recipients: Optional[
        list["SendEmailResponseMessageToRecipientsArrayItemRef"]
    ] = Field(alias="toRecipients", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SendEmailResponseMessage"], src_dict: Dict[str, Any]):
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
