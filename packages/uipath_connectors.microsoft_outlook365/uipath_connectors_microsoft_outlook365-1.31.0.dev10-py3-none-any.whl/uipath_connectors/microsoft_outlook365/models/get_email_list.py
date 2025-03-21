from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_email_list_body import GetEmailListBody
from ..models.get_email_list_end_date_time import GetEmailListEndDateTime
from ..models.get_email_list_flag import GetEmailListFlag
from ..models.get_email_list_from import GetEmailListFrom
from ..models.get_email_list_location import GetEmailListLocation
from ..models.get_email_list_odata import GetEmailListOdata
from ..models.get_email_list_previous_end_date_time import (
    GetEmailListPreviousEndDateTime,
)
from ..models.get_email_list_previous_start_date_time import (
    GetEmailListPreviousStartDateTime,
)
from ..models.get_email_list_recurrence import GetEmailListRecurrence
from ..models.get_email_list_sender import GetEmailListSender
from ..models.get_email_list_start_date_time import GetEmailListStartDateTime
from ..models.get_email_list_to_recipients_array_item_ref import (
    GetEmailListToRecipientsArrayItemRef,
)
import datetime


class GetEmailList(BaseModel):
    """
    Attributes:
        odata (Optional[GetEmailListOdata]):
        body (Optional[GetEmailListBody]):
        body_preview (Optional[str]): A short preview of the email's content. Example: Textbox.
        change_key (Optional[str]): A key indicating the version of the email for tracking changes. Example:
                CQAAABYAAAB8H2U+2gSPS6CGFwCo8hoKAAEvP9xX.
        conversation_id (Optional[str]): Unique identifier for the email conversation thread. Example:
                AAQkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNAAQANWyaIA5jwdLkMGD6LvBF3U=.
        conversation_index (Optional[str]): Unique identifier for the position of the email in a thread. Example:
                AQHblA661bJogDmPB0uQwYPou8EXdQ==.
        created_date_time (Optional[datetime.datetime]): The date and time when the email was created. Example:
                2025-03-13T11:55:24Z.
        end_date_time (Optional[GetEmailListEndDateTime]):
        flag (Optional[GetEmailListFlag]):
        from_ (Optional[GetEmailListFrom]):
        has_attachments (Optional[bool]): Indicates whether the email contains any attachments. Example: True.
        id (Optional[str]): A unique identifier for the email. Example: AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRl
                ZTQyNABGAAAAAACheKuSte_nRYh5zSjSpULXBwB8H2U_2gSPS6CGFwCo8hoKAAAAAAEMAAB8H2U_2gSPS6CGFwCo8hoKAAEvmKSeAAA=.
        importance (Optional[str]): Indicates the priority level of the email, such as high, normal, or low. Example:
                normal.
        inference_classification (Optional[str]): The classification of the email based on inferred importance. Example:
                focused.
        internet_message_id (Optional[str]): A unique identifier for the email message on the internet. Example:
                <AM9PR02MB68031CAC547B184FB5900423FDD32@AM9PR02MB6803.eurprd02.prod.outlook.com>.
        is_all_day (Optional[bool]): Indicates whether the event lasts for the entire day.
        is_delegated (Optional[bool]): Indicates whether the action is performed by a delegate.
        is_draft (Optional[bool]): Indicates whether the email is saved as a draft.
        is_out_of_date (Optional[bool]): Indicates whether the information is outdated or not.
        is_read (Optional[bool]): Shows whether the email has been read or is still marked as unread. Example: True.
        is_read_receipt_requested (Optional[bool]): Indicates if a read receipt is requested for the email.
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the email was last modified.
                Example: 2025-03-13T12:11:48Z.
        location (Optional[GetEmailListLocation]):
        meeting_message_type (Optional[str]): Describes the type of message related to the meeting. Example:
                meetingCancelled.
        meeting_request_type (Optional[str]): Specifies the type of meeting request, such as new or update. Example:
                fullUpdate.
        parent_folder_id (Optional[str]): The unique identifier of the parent folder containing the email. Example: AAMk
                ADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNAAuAAAAAACheKuSte_nRYh5zSjSpULXAQB8H2U_2gSPS6CGFwCo8hoKAAAAAAEM
                AAA=.
        previous_end_date_time (Optional[GetEmailListPreviousEndDateTime]):
        previous_start_date_time (Optional[GetEmailListPreviousStartDateTime]):
        received_date_time (Optional[datetime.datetime]): The date and time when the email was received. Example:
                2025-03-13T11:55:24Z.
        recurrence (Optional[GetEmailListRecurrence]):
        response_requested (Optional[bool]): Indicates if a response is requested from the recipient. Example: True.
        response_type (Optional[str]): Indicates the type of response expected from the API. Example: declined.
        sender (Optional[GetEmailListSender]):
        sent_date_time (Optional[datetime.datetime]): The date and time when the email was sent. Example:
                2025-03-13T11:55:20Z.
        start_date_time (Optional[GetEmailListStartDateTime]):
        subject (Optional[str]): The subject line of the email message. Example: Testreplyv4.
        to_recipients (Optional[list['GetEmailListToRecipientsArrayItemRef']]):
        type_ (Optional[str]): Specifies the type of event or action being performed. Example: seriesMaster.
        web_link (Optional[str]): A URL that directs you to view the email online. Example: https://outlook.office365.co
                m/owa/?ItemID=AAMkADJmOGNjOTYwLWMzOWUtNGEzMC05MTViLTVmMjU3ZmRlZTQyNABGAAAAAACheKuSte%2BnRYh5zSjSpULXBwB8H2U%2B2g
                SPS6CGFwCo8hoKAAAAAAEMAAB8H2U%2B2gSPS6CGFwCo8hoKAAEvmKSeAAA%3D&exvsurl=1&viewmodel=ReadMessageItem.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    odata: Optional["GetEmailListOdata"] = Field(alias="@odata", default=None)
    body: Optional["GetEmailListBody"] = Field(alias="body", default=None)
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    conversation_id: Optional[str] = Field(alias="conversationId", default=None)
    conversation_index: Optional[str] = Field(alias="conversationIndex", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    end_date_time: Optional["GetEmailListEndDateTime"] = Field(
        alias="endDateTime", default=None
    )
    flag: Optional["GetEmailListFlag"] = Field(alias="flag", default=None)
    from_: Optional["GetEmailListFrom"] = Field(alias="from", default=None)
    has_attachments: Optional[bool] = Field(alias="hasAttachments", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[str] = Field(alias="importance", default=None)
    inference_classification: Optional[str] = Field(
        alias="inferenceClassification", default=None
    )
    internet_message_id: Optional[str] = Field(alias="internetMessageId", default=None)
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=None)
    is_delegated: Optional[bool] = Field(alias="isDelegated", default=None)
    is_draft: Optional[bool] = Field(alias="isDraft", default=None)
    is_out_of_date: Optional[bool] = Field(alias="isOutOfDate", default=None)
    is_read: Optional[bool] = Field(alias="isRead", default=None)
    is_read_receipt_requested: Optional[bool] = Field(
        alias="isReadReceiptRequested", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    location: Optional["GetEmailListLocation"] = Field(alias="location", default=None)
    meeting_message_type: Optional[str] = Field(
        alias="meetingMessageType", default=None
    )
    meeting_request_type: Optional[str] = Field(
        alias="meetingRequestType", default=None
    )
    parent_folder_id: Optional[str] = Field(alias="parentFolderId", default=None)
    previous_end_date_time: Optional["GetEmailListPreviousEndDateTime"] = Field(
        alias="previousEndDateTime", default=None
    )
    previous_start_date_time: Optional["GetEmailListPreviousStartDateTime"] = Field(
        alias="previousStartDateTime", default=None
    )
    received_date_time: Optional[datetime.datetime] = Field(
        alias="receivedDateTime", default=None
    )
    recurrence: Optional["GetEmailListRecurrence"] = Field(
        alias="recurrence", default=None
    )
    response_requested: Optional[bool] = Field(alias="responseRequested", default=None)
    response_type: Optional[str] = Field(alias="responseType", default=None)
    sender: Optional["GetEmailListSender"] = Field(alias="sender", default=None)
    sent_date_time: Optional[datetime.datetime] = Field(
        alias="sentDateTime", default=None
    )
    start_date_time: Optional["GetEmailListStartDateTime"] = Field(
        alias="startDateTime", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[list["GetEmailListToRecipientsArrayItemRef"]] = Field(
        alias="toRecipients", default=None
    )
    type_: Optional[str] = Field(alias="type", default=None)
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetEmailList"], src_dict: Dict[str, Any]):
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
