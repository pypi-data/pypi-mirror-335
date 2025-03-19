from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.reply_to_email_response_message_email_classification import (
    ReplyToEmailResponseMessageEmailClassification,
)
from ..models.reply_to_email_response_message_importance import (
    ReplyToEmailResponseMessageImportance,
)


class ReplyToEmailResponseMessage(BaseModel):
    """
    Attributes:
        importance (Optional[ReplyToEmailResponseMessageImportance]): Indicates the priority level of the email message.
                Example: high.
        inference_classification (Optional[ReplyToEmailResponseMessageEmailClassification]): The classification of the
                email based on inferred importance.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    importance: Optional[ReplyToEmailResponseMessageImportance] = Field(
        alias="importance", default=None
    )
    inference_classification: Optional[
        ReplyToEmailResponseMessageEmailClassification
    ] = Field(alias="inferenceClassification", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ReplyToEmailResponseMessage"], src_dict: Dict[str, Any]):
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
