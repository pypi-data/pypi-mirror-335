from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.move_email_response_body import MoveEmailResponseBody
from ..models.move_email_response_flag import MoveEmailResponseFlag
from ..models.move_email_response_from import MoveEmailResponseFrom
from ..models.move_email_response_sender import MoveEmailResponseSender
from ..models.move_email_response_to_recipients_array_item_ref import (
    MoveEmailResponseToRecipientsArrayItemRef,
)
import datetime


class MoveEmailResponse(BaseModel):
    """
    Attributes:
        body (Optional[MoveEmailResponseBody]):
        body_preview (Optional[str]): A short preview of the email's content. Example: Test1.
        change_key (Optional[str]): A key indicating the current version of the email. Example:
                CQAAABYAAAB8H2U+2gSPS6CGFwCo8hoKAAELA6q1.
        conversation_id (Optional[str]): A unique identifier for the email conversation thread. Example:
                AAQkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNAAQAAS8lP6HT3pHpyyhBOJfv6k=.
        conversation_index (Optional[str]): A unique identifier for the email's position in a conversation. Example:
                AQHbSizuBLyU/odPekenLKEE4l+/qQ==.
        created_date_time (Optional[datetime.datetime]): The date and time when the email was created. Example:
                2024-12-09T11:24:58Z.
        flag (Optional[MoveEmailResponseFlag]):
        from_ (Optional[MoveEmailResponseFrom]):
        has_attachments (Optional[bool]): Indicates if the email contains any attachments.
        id (Optional[str]): Unique identifier for the email within the system. Example: AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05
                MTViLTVmMjU3ZmRlZTQyNABGAAAAAACheKuSte_nRYh5zSjSpULXBwB8H2U_2gSPS6CGFwCo8hoKAAAAAAEKAAB8H2U_2gSPS6CGFwCo8hoKAAEL
                Sg9LAAA=.
        importance (Optional[str]): The priority level of the email, such as high, normal, or low. Example: normal.
        inference_classification (Optional[str]): The classification of the email based on inferred importance. Example:
                focused.
        internet_message_id (Optional[str]): Unique identifier for the email message. Example:
                <AS8PR02MB68077E6860E8D4D4F663066BFD3C2@AS8PR02MB6807.eurprd02.prod.outlook.com>.
        is_draft (Optional[bool]): Shows if the email is currently a draft.
        is_read (Optional[bool]): Indicates whether the email has been read.
        is_read_receipt_requested (Optional[bool]): Indicates if a read receipt is requested for the email.
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the email was last modified.
                Example: 2025-01-16T09:53:48Z.
        odata_context (Optional[str]): The URL that provides context for the email data. Example:
                https://graph.microsoft.com/v1.0/$metadata#users('dfed9647-6382-4306-be51-0b2e0ae176a8')/messages/$entity.
        odata_etag (Optional[str]): A unique identifier for the version of the email. Example:
                W/"CQAAABYAAAB8H2U+2gSPS6CGFwCo8hoKAAELA6q1".
        parent_folder_id (Optional[str]): The unique identifier of the folder containing the email. Example: AAMkADJmOGN
                jOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNAAuAAAAAACheKuSte_nRYh5zSjSpULXAQB8H2U_2gSPS6CGFwCo8hoKAAAAAAEKAAA=.
        received_date_time (Optional[datetime.datetime]): The date and time when the email was received. Example:
                2024-12-09T11:24:58Z.
        sender (Optional[MoveEmailResponseSender]):
        sent_date_time (Optional[datetime.datetime]): The date and time when the email was sent. Example:
                2024-12-09T11:24:50Z.
        subject (Optional[str]): The subject line of the email message. Example: Test1.
        to_recipients (Optional[list['MoveEmailResponseToRecipientsArrayItemRef']]):
        web_link (Optional[str]): A URL link to access the email in a web browser. Example: https://outlook.office365.co
                m/owa/?ItemID=AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNABGAAAAAACheKuSte%2BnRYh5zSjSpULXBwB8H2U%2B2g
                SPS6CGFwCo8hoKAAAAAAEKAAB8H2U%2B2gSPS6CGFwCo8hoKAAELSg9LAAA%3D&exvsurl=1&viewmodel=ReadMessageItem.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: Optional["MoveEmailResponseBody"] = Field(alias="body", default=None)
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    conversation_id: Optional[str] = Field(alias="conversationId", default=None)
    conversation_index: Optional[str] = Field(alias="conversationIndex", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    flag: Optional["MoveEmailResponseFlag"] = Field(alias="flag", default=None)
    from_: Optional["MoveEmailResponseFrom"] = Field(alias="from", default=None)
    has_attachments: Optional[bool] = Field(alias="hasAttachments", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    inference_classification: Optional[str] = Field(
        alias="inferenceClassification", default=None
    )
    internet_message_id: Optional[str] = Field(alias="internetMessageId", default=None)
    is_draft: Optional[bool] = Field(alias="isDraft", default=None)
    is_read: Optional[bool] = Field(alias="isRead", default=None)
    is_read_receipt_requested: Optional[bool] = Field(
        alias="isReadReceiptRequested", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    odata_context: Optional[str] = Field(alias="odataContext", default=None)
    odata_etag: Optional[str] = Field(alias="odataEtag", default=None)
    parent_folder_id: Optional[str] = Field(alias="parentFolderId", default=None)
    received_date_time: Optional[datetime.datetime] = Field(
        alias="receivedDateTime", default=None
    )
    sender: Optional["MoveEmailResponseSender"] = Field(alias="sender", default=None)
    sent_date_time: Optional[datetime.datetime] = Field(
        alias="sentDateTime", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[list["MoveEmailResponseToRecipientsArrayItemRef"]] = Field(
        alias="toRecipients", default=None
    )
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["MoveEmailResponse"], src_dict: Dict[str, Any]):
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
