from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.list_email_importance import ListEmailImportance
from ..models.list_email_inference_classification import (
    ListEmailInferenceClassification,
)
import datetime
from ..models.list_email_previous_location import ListEmailPreviousLocation
from ..models.list_email_to_recipients_array_item_ref import (
    ListEmailToRecipientsArrayItemRef,
)
from ..models.list_email_previous_end_date_time import ListEmailPreviousEndDateTime
from ..models.list_email_bcc_recipients_array_item_ref import (
    ListEmailBccRecipientsArrayItemRef,
)
from ..models.list_email_previous_start_date_time import ListEmailPreviousStartDateTime
from ..models.list_email_reply_to_array_item_ref import ListEmailReplyToArrayItemRef
from ..models.list_email_recurrence import ListEmailRecurrence
from ..models.list_email_cc_recipients_array_item_ref import (
    ListEmailCcRecipientsArrayItemRef,
)
from ..models.list_email_location import ListEmailLocation
from ..models.list_email_body import ListEmailBody
from ..models.list_email_start_date_time import ListEmailStartDateTime
from ..models.list_email_sender import ListEmailSender
from ..models.list_email_flag import ListEmailFlag
from ..models.list_email_from import ListEmailFrom
from ..models.list_email_end_date_time import ListEmailEndDateTime


class ListEmail(BaseModel):
    """
    Attributes:
        bcc_recipients (Optional[list['ListEmailBccRecipientsArrayItemRef']]):
        body (Optional[ListEmailBody]):
        body_preview (Optional[str]):
        categories (Optional[list[str]]):
        cc_recipients (Optional[list['ListEmailCcRecipientsArrayItemRef']]):
        change_key (Optional[str]):
        conversation_id (Optional[str]):
        conversation_index (Optional[str]):
        created_date_time (Optional[datetime.datetime]):
        end_date_time (Optional[ListEmailEndDateTime]):
        flag (Optional[ListEmailFlag]):
        from_ (Optional[ListEmailFrom]):
        has_attachments (Optional[bool]):
        id (Optional[str]):
        importance (Optional[ListEmailImportance]):
        inference_classification (Optional[ListEmailInferenceClassification]):
        internet_message_id (Optional[str]):
        is_all_day (Optional[bool]):
        is_delegated (Optional[bool]):
        is_delivery_receipt_requested (Optional[bool]):
        is_draft (Optional[bool]):
        is_out_of_date (Optional[bool]):
        is_read (Optional[bool]):
        is_read_receipt_requested (Optional[bool]):
        last_modified_date_time (Optional[datetime.datetime]):
        location (Optional[ListEmailLocation]):
        meeting_message_type (Optional[str]):
        meeting_request_type (Optional[str]):
        parent_folder_id (Optional[str]):
        parent_folder_name (Optional[str]):
        previous_end_date_time (Optional[ListEmailPreviousEndDateTime]):
        previous_location (Optional[ListEmailPreviousLocation]):
        previous_start_date_time (Optional[ListEmailPreviousStartDateTime]):
        received_date_time (Optional[datetime.datetime]):
        recurrence (Optional[ListEmailRecurrence]):
        reply_to (Optional[list['ListEmailReplyToArrayItemRef']]):
        response_requested (Optional[bool]):
        sender (Optional[ListEmailSender]):
        sent_date_time (Optional[datetime.datetime]):
        start_date_time (Optional[ListEmailStartDateTime]):
        subject (Optional[str]):
        to_recipients (Optional[list['ListEmailToRecipientsArrayItemRef']]):
        type_ (Optional[str]):
        web_link (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    bcc_recipients: Optional[list["ListEmailBccRecipientsArrayItemRef"]] = Field(
        alias="bccRecipients", default=None
    )
    body: Optional["ListEmailBody"] = Field(alias="body", default=None)
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    categories: Optional[list[str]] = Field(alias="categories", default=None)
    cc_recipients: Optional[list["ListEmailCcRecipientsArrayItemRef"]] = Field(
        alias="ccRecipients", default=None
    )
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    conversation_id: Optional[str] = Field(alias="conversationId", default=None)
    conversation_index: Optional[str] = Field(alias="conversationIndex", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    end_date_time: Optional["ListEmailEndDateTime"] = Field(
        alias="endDateTime", default=None
    )
    flag: Optional["ListEmailFlag"] = Field(alias="flag", default=None)
    from_: Optional["ListEmailFrom"] = Field(alias="from", default=None)
    has_attachments: Optional[bool] = Field(alias="hasAttachments", default=None)
    id: Optional[str] = Field(alias="id", default=None)
    importance: Optional[ListEmailImportance] = Field(alias="importance", default=None)
    inference_classification: Optional[ListEmailInferenceClassification] = Field(
        alias="inferenceClassification", default=None
    )
    internet_message_id: Optional[str] = Field(alias="internetMessageId", default=None)
    is_all_day: Optional[bool] = Field(alias="isAllDay", default=None)
    is_delegated: Optional[bool] = Field(alias="isDelegated", default=None)
    is_delivery_receipt_requested: Optional[bool] = Field(
        alias="isDeliveryReceiptRequested", default=None
    )
    is_draft: Optional[bool] = Field(alias="isDraft", default=None)
    is_out_of_date: Optional[bool] = Field(alias="isOutOfDate", default=None)
    is_read: Optional[bool] = Field(alias="isRead", default=None)
    is_read_receipt_requested: Optional[bool] = Field(
        alias="isReadReceiptRequested", default=None
    )
    last_modified_date_time: Optional[datetime.datetime] = Field(
        alias="lastModifiedDateTime", default=None
    )
    location: Optional["ListEmailLocation"] = Field(alias="location", default=None)
    meeting_message_type: Optional[str] = Field(
        alias="meetingMessageType", default=None
    )
    meeting_request_type: Optional[str] = Field(
        alias="meetingRequestType", default=None
    )
    parent_folder_id: Optional[str] = Field(alias="parentFolderId", default=None)
    parent_folder_name: Optional[str] = Field(alias="parentFolderName", default=None)
    previous_end_date_time: Optional["ListEmailPreviousEndDateTime"] = Field(
        alias="previousEndDateTime", default=None
    )
    previous_location: Optional["ListEmailPreviousLocation"] = Field(
        alias="previousLocation", default=None
    )
    previous_start_date_time: Optional["ListEmailPreviousStartDateTime"] = Field(
        alias="previousStartDateTime", default=None
    )
    received_date_time: Optional[datetime.datetime] = Field(
        alias="receivedDateTime", default=None
    )
    recurrence: Optional["ListEmailRecurrence"] = Field(
        alias="recurrence", default=None
    )
    reply_to: Optional[list["ListEmailReplyToArrayItemRef"]] = Field(
        alias="replyTo", default=None
    )
    response_requested: Optional[bool] = Field(alias="responseRequested", default=None)
    sender: Optional["ListEmailSender"] = Field(alias="sender", default=None)
    sent_date_time: Optional[datetime.datetime] = Field(
        alias="sentDateTime", default=None
    )
    start_date_time: Optional["ListEmailStartDateTime"] = Field(
        alias="startDateTime", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[list["ListEmailToRecipientsArrayItemRef"]] = Field(
        alias="toRecipients", default=None
    )
    type_: Optional[str] = Field(alias="type", default=None)
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ListEmail"], src_dict: Dict[str, Any]):
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
