from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.archive_email_response_body import ArchiveEmailResponseBody
from ..models.archive_email_response_flag import ArchiveEmailResponseFlag
from ..models.archive_email_response_from import ArchiveEmailResponseFrom
from ..models.archive_email_response_sender import ArchiveEmailResponseSender
from ..models.archive_email_response_to_recipients_array_item_ref import (
    ArchiveEmailResponseToRecipientsArrayItemRef,
)
import datetime


class ArchiveEmailResponse(BaseModel):
    """
    Attributes:
        body (Optional[ArchiveEmailResponseBody]):
        body_preview (Optional[str]): A short preview of the email's content. Example: AttachmentInEmail.
        change_key (Optional[str]): Identifies the version of the email item. Example:
                CQAAABYAAAB8H2U+2gSPS6CGFwCo8hoKAAEPwhAn.
        conversation_id (Optional[str]): A unique identifier for the email conversation thread. Example:
                AAQkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNAAQACcCXuBGNp9Nvb7IFWPiaCE=.
        conversation_index (Optional[str]): A unique identifier for the email's position in a thread. Example:
                AQHbaKSBJwJe4EY2n029vsgVY+JoIQ==.
        created_date_time (Optional[datetime.datetime]): The date and time when the email was created. Example:
                2025-01-17T05:57:20Z.
        flag (Optional[ArchiveEmailResponseFlag]):
        from_ (Optional[ArchiveEmailResponseFrom]):
        has_attachments (Optional[bool]): Indicates if the email has attachments. Example: True.
        id (Optional[str]): The unique identifier for the email. Example: AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3Zm
                RlZTQyNABGAAAAAACheKuSte_nRYh5zSjSpULXBwB8H2U_2gSPS6CGFwCo8hoKAAAAAAETAAB8H2U_2gSPS6CGFwCo8hoKAAEQC3yRAAA=.
        importance (Optional[str]): The priority level of the email, such as high, normal, or low. Example: normal.
        inference_classification (Optional[str]): The classification of the email based on inferred importance. Example:
                focused.
        internet_message_id (Optional[str]): A unique identifier for the email message on the internet. Example:
                <AS8PR02MB6807EAA106E7AE4C5CF84BABFD1B2@AS8PR02MB6807.eurprd02.prod.outlook.com>.
        is_draft (Optional[bool]): Indicates whether the email is a draft.
        is_read (Optional[bool]): Indicates whether the email has been read.
        is_read_receipt_requested (Optional[bool]): Indicates if a read receipt is requested.
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the email was last modified.
                Example: 2025-01-23T07:33:17Z.
        parent_folder_id (Optional[str]): The unique identifier of the folder containing the email. Example: AAMkADJmOGN
                jOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNAAuAAAAAACheKuSte_nRYh5zSjSpULXAQB8H2U_2gSPS6CGFwCo8hoKAAAAAAETAAA=.
        received_date_time (Optional[datetime.datetime]): Indicates when the email was received. Example:
                2025-01-17T05:57:21Z.
        sender (Optional[ArchiveEmailResponseSender]):
        sent_date_time (Optional[datetime.datetime]): The date and time when the email was sent. Example:
                2025-01-17T05:57:17Z.
        subject (Optional[str]): The subject line of the email. Example: TestWithAttachment.
        to_recipients (Optional[list['ArchiveEmailResponseToRecipientsArrayItemRef']]):
        web_link (Optional[str]): A URL link to access the email in a web browser. Example: https://outlook.office365.co
                m/owa/?ItemID=AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNABGAAAAAACheKuSte%2BnRYh5zSjSpULXBwB8H2U%2B2g
                SPS6CGFwCo8hoKAAAAAAETAAB8H2U%2B2gSPS6CGFwCo8hoKAAEQC3yRAAA%3D&exvsurl=1&viewmodel=ReadMessageItem.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    body: Optional["ArchiveEmailResponseBody"] = Field(alias="body", default=None)
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    conversation_id: Optional[str] = Field(alias="conversationId", default=None)
    conversation_index: Optional[str] = Field(alias="conversationIndex", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    flag: Optional["ArchiveEmailResponseFlag"] = Field(alias="flag", default=None)
    from_: Optional["ArchiveEmailResponseFrom"] = Field(alias="from", default=None)
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
    parent_folder_id: Optional[str] = Field(alias="parentFolderId", default=None)
    received_date_time: Optional[datetime.datetime] = Field(
        alias="receivedDateTime", default=None
    )
    sender: Optional["ArchiveEmailResponseSender"] = Field(alias="sender", default=None)
    sent_date_time: Optional[datetime.datetime] = Field(
        alias="sentDateTime", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[list["ArchiveEmailResponseToRecipientsArrayItemRef"]] = (
        Field(alias="toRecipients", default=None)
    )
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ArchiveEmailResponse"], src_dict: Dict[str, Any]):
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
