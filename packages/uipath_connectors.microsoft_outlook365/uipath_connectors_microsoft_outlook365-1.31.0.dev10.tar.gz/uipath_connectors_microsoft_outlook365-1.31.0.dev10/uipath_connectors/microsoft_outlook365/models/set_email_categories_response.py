from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.set_email_categories_response_body import SetEmailCategoriesResponseBody
from ..models.set_email_categories_response_flag import SetEmailCategoriesResponseFlag
from ..models.set_email_categories_response_from import SetEmailCategoriesResponseFrom
from ..models.set_email_categories_response_reply_to_array_item_ref import (
    SetEmailCategoriesResponseReplyToArrayItemRef,
)
from ..models.set_email_categories_response_sender import (
    SetEmailCategoriesResponseSender,
)
from ..models.set_email_categories_response_to_recipients_array_item_ref import (
    SetEmailCategoriesResponseToRecipientsArrayItemRef,
)
import datetime


class SetEmailCategoriesResponse(BaseModel):
    """
    Attributes:
        categories (list[str]):
        body (Optional[SetEmailCategoriesResponseBody]):
        body_preview (Optional[str]): A short preview of the email's content. Example: Thank you for contacting UiPath
                INC (Development Account 18) Customer Support.

                Your request for assistance has been received. Case #4738 - "dUluNp" has been created for you. A member of our
                customer care team will respond to your case as soon as possib.
        categories_to_remove (Optional[list[str]]):
        change_key (Optional[str]): A key indicating the version of the email item. Example:
                CQAAABYAAAChYKqlW9nAQ7RRjRl2FNi0AAOYOJTi.
        conversation_id (Optional[str]): A unique identifier for the email conversation thread. Example:
                AAQkADQ2NDRhMTQxLWUyNzctNDE1MS04YjMwLTc0NzZjYmY5ODVlOAAQAIIEmmrwZ3ZChxDtRmblMno=.
        conversation_index (Optional[str]): An index that helps track the email's conversation thread. Example:
                AQHbbJdRggSaavBndkKHEO1GZuUyeg==.
        created_date_time (Optional[datetime.datetime]): The date and time when the email was created. Example:
                2025-01-22T06:31:50Z.
        flag (Optional[SetEmailCategoriesResponseFlag]):
        from_ (Optional[SetEmailCategoriesResponseFrom]):
        has_attachments (Optional[bool]): Indicates whether the email has any attachments.
        id (Optional[str]): A unique identifier for the email message. Example: AAMkADQ2NDRhMTQxLWUyNzctNDE1MS04YjMwLTc0
                NzZjYmY5ODVlOABGAAAAAAB7-
                0ulZn6bT6aA0bxus58UBwChYKqlW9nAQ7RRjRl2FNi0AAAAAAEMAAChYKqlW9nAQ7RRjRl2FNi0AAOal27lAAA=.
        importance (Optional[str]): The priority level of the email, such as low, normal, or high. Example: normal.
        inference_classification (Optional[str]): The classification of the email based on inferred importance. Example:
                other.
        internet_message_id (Optional[str]): Unique identifier for the email message. Example:
                <8jd8ctod03484x1wq6zgoqeo8lrpgkvxxqx9uvteuz2tno5067cmqs1wre3q8id6@netsuite.com>.
        is_draft (Optional[bool]): Shows if the email is currently a draft.
        is_read (Optional[bool]): Indicates whether the email has been read. Example: True.
        is_read_receipt_requested (Optional[bool]): Indicates if a read receipt is requested for the email.
        last_modified_date_time (Optional[datetime.datetime]): The date and time when the email was last modified.
                Example: 2025-01-22T06:51:26Z.
        parent_folder_id (Optional[str]): The unique identifier of the folder containing the email. Example: AAMkADQ2NDR
                hMTQxLWUyNzctNDE1MS04YjMwLTc0NzZjYmY5ODVlOAAuAAAAAAB7-0ulZn6bT6aA0bxus58UAQChYKqlW9nAQ7RRjRl2FNi0AAAAAAEMAAA=.
        received_date_time (Optional[datetime.datetime]): The date and time when the email was received. Example:
                2025-01-22T06:31:50Z.
        reply_to (Optional[list['SetEmailCategoriesResponseReplyToArrayItemRef']]):
        sender (Optional[SetEmailCategoriesResponseSender]):
        sent_date_time (Optional[datetime.datetime]): The date and time when the email was sent. Example:
                2025-01-22T06:31:30Z.
        subject (Optional[str]): The subject line of the email message. Example: Case # 4738 Created: dUluNp (originally
                To: tylerperez@example.org) (originally envelope recipients: tylerperez@example.org).
        to_recipients (Optional[list['SetEmailCategoriesResponseToRecipientsArrayItemRef']]):
        web_link (Optional[str]): A URL link to access the email in a web browser. Example: https://outlook.office365.co
                m/owa/?ItemID=AAMkADQ2NDRhMTQxLWUyNzctNDE1MS04YjMwLTc0NzZjYmY5ODVlOABGAAAAAAB7%2F0ulZn6bT6aA0bxus58UBwChYKqlW9nA
                Q7RRjRl2FNi0AAAAAAEMAAChYKqlW9nAQ7RRjRl2FNi0AAOal27lAAA%3D&exvsurl=1&viewmodel=ReadMessageItem.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    categories: list[str] = Field(alias="categories")
    body: Optional["SetEmailCategoriesResponseBody"] = Field(alias="body", default=None)
    body_preview: Optional[str] = Field(alias="bodyPreview", default=None)
    categories_to_remove: Optional[list[str]] = Field(
        alias="categoriesToRemove", default=None
    )
    change_key: Optional[str] = Field(alias="changeKey", default=None)
    conversation_id: Optional[str] = Field(alias="conversationId", default=None)
    conversation_index: Optional[str] = Field(alias="conversationIndex", default=None)
    created_date_time: Optional[datetime.datetime] = Field(
        alias="createdDateTime", default=None
    )
    flag: Optional["SetEmailCategoriesResponseFlag"] = Field(alias="flag", default=None)
    from_: Optional["SetEmailCategoriesResponseFrom"] = Field(
        alias="from", default=None
    )
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
    reply_to: Optional[list["SetEmailCategoriesResponseReplyToArrayItemRef"]] = Field(
        alias="replyTo", default=None
    )
    sender: Optional["SetEmailCategoriesResponseSender"] = Field(
        alias="sender", default=None
    )
    sent_date_time: Optional[datetime.datetime] = Field(
        alias="sentDateTime", default=None
    )
    subject: Optional[str] = Field(alias="subject", default=None)
    to_recipients: Optional[
        list["SetEmailCategoriesResponseToRecipientsArrayItemRef"]
    ] = Field(alias="toRecipients", default=None)
    web_link: Optional[str] = Field(alias="webLink", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SetEmailCategoriesResponse"], src_dict: Dict[str, Any]):
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
