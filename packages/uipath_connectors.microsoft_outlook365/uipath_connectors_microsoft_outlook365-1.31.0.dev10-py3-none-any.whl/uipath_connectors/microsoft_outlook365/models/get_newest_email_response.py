from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_newest_email_response_body import GetNewestEmailResponseBody
from ..models.get_newest_email_response_flag import GetNewestEmailResponseFlag
from ..models.get_newest_email_response_from import GetNewestEmailResponseFrom
from ..models.get_newest_email_response_sender import GetNewestEmailResponseSender
from ..models.get_newest_email_response_to_recipients_array_item_ref import (
    GetNewestEmailResponseToRecipientsArrayItemRef,
)
import datetime


class GetNewestEmailResponse(BaseModel):
    """
    Attributes:
        body (Optional[GetNewestEmailResponseBody]):
        body_preview (Optional[str]): A short preview of the email's content. Example: new comment
                ________________________________
                From: UiPath INC (Development Account 18) (cedeveloper@uipath.com) <system@sent-via.netsuite.com>
                Sent: Wednesday, January 22, 2025 6:31:30 AM
                To: CE Developer <CEdeveloper@uipath.com>
                Subject: Case # 4738.
        change_key (Optional[str]): A unique identifier for the current version of the email. Example:
                CQAAABYAAAChYKqlW9nAQ7RRjRl2FNi0AAObHBXw.
        conversation_id (Optional[str]): A unique identifier for the email conversation thread. Example:
                AAQkADQ2NDRhMTQxLWUyNzctNDE1MS04YjMwLTc0NzZjYmY5ODVlOAAQAIIEmmrwZ3ZChxDtRmblMno=.
        conversation_index (Optional[str]): A unique identifier for the email's position in a thread. Example:
                AQHbbJdRggSaavBndkKHEO1GZuUyerMjo3Cp.
        created_date_time (Optional[datetime.datetime]): The date and time when the email was created. Example:
                2025-01-23T02:27:12Z.
        flag (Optional[GetNewestEmailResponseFlag]):
        from_ (Optional[GetNewestEmailResponseFrom]):
        has_attachments (Optional[bool]): Indicates if the email contains attachments.
        id (Optional[str]): The unique identifier for the email. Example: AAMkADQ2NDRhMTQxLWUyNzctNDE1MS04YjMwLTc0NzZjYm
                Y5ODVlOABGAAAAAAB7-0ulZn6bT6aA0bxus58UBwChYKqlW9nAQ7RRjRl2FNi0AAAAAAEPAAChYKqlW9nAQ7RRjRl2FNi0AAOdfbo9AAA=.
        importance (Optional[str]): The priority level of the email, such as high, normal, or low. Example: normal.
        inference_classification (Optional[str]): The classification of the email based on its content. Example:
                focused.
        internet_message_id (Optional[str]): A unique identifier for the email message. Example:
                <DB6PR02MB3016E80ACCEE24FD762EEA75EDE02@DB6PR02MB3016.eurprd02.prod.outlook.com>.
        is_delivery_receipt_requested (Optional[bool]): Indicates if a delivery receipt was requested for the email.
        is_draft (Optional[bool]): Indicates whether the email is a draft. Example: True.
        is_read (Optional[bool]): Indicates whether the email has been read. Example: True.
        is_read_receipt_requested (Optional[bool]): Indicates if a read receipt is requested.
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the email was last modified.
                Example: 2025-01-23T02:27:12Z.
        parent_folder_id (Optional[str]): The unique identifier of the folder containing the email. Example: AAMkADQ2NDR
                hMTQxLWUyNzctNDE1MS04YjMwLTc0NzZjYmY5ODVlOAAuAAAAAAB7-0ulZn6bT6aA0bxus58UAQChYKqlW9nAQ7RRjRl2FNi0AAAAAAEPAAA=.
        received_date_time (Optional[datetime.datetime]): The date and time when the email was received. Example:
                2025-01-23T02:27:12Z.
        sender (Optional[GetNewestEmailResponseSender]):
        sent_date_time (Optional[datetime.datetime]): The date and time when the email was sent. Example:
                2025-01-23T02:27:12Z.
        subject (Optional[str]): The subject line of the email message. Example: FW: Case # 4738 Created: dUluNp
                (originally To: tylerperez@example.org) (originally envelope recipients: tylerperez@example.org).
        to_recipients (Optional[list['GetNewestEmailResponseToRecipientsArrayItemRef']]):
        web_link (Optional[str]): A URL link to view the email in a web browser. Example: https://outlook.office365.com/
                owa/?ItemID=AAMkADQ2NDRhMTQxLWUyNzctNDE1MS04YjMwLTc0NzZjYmY5ODVlOABGAAAAAAB7%2F0ulZn6bT6aA0bxus58UBwChYKqlW9nAQ7
                RRjRl2FNi0AAAAAAEPAAChYKqlW9nAQ7RRjRl2FNi0AAOdfbo9AAA%3D&exvsurl=1&viewmodel=ReadMessageItem.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: Optional["GetNewestEmailResponseBody"] = Field(alias="body", default=None)
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    conversation_id: Optional[str] = Field(alias="conversationId", default=None)
    conversation_index: Optional[str] = Field(alias="conversationIndex", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    flag: Optional["GetNewestEmailResponseFlag"] = Field(alias="flag", default=None)
    from_: Optional["GetNewestEmailResponseFrom"] = Field(alias="from", default=None)
    has_attachments: Optional[bool] = Field(alias="hasAttachments", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    inference_classification: Optional[str] = Field(
        alias="inferenceClassification", default=None
    )
    internet_message_id: Optional[str] = Field(alias="internetMessageId", default=None)
    is_delivery_receipt_requested: Optional[bool] = Field(
        alias="isDeliveryReceiptRequested", default=None
    )
    is_draft: Optional[bool] = Field(alias="isDraft", default=None)
    is_read: Optional[bool] = Field(alias="isRead", default=None)
    is_read_receipt_requested: Optional[bool] = Field(
        alias="isReadReceiptRequested", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    parent_folder_id: Optional[str] = Field(alias="parentFolderId", default=None)
    received_date_time: Optional[datetime.datetime] = Field(
        alias="receivedDateTime", default=None
    )
    sender: Optional["GetNewestEmailResponseSender"] = Field(
        alias="sender", default=None
    )
    sent_date_time: Optional[datetime.datetime] = Field(
        alias="sentDateTime", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[list["GetNewestEmailResponseToRecipientsArrayItemRef"]] = (
        Field(alias="toRecipients", default=None)
    )
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetNewestEmailResponse"], src_dict: Dict[str, Any]):
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
