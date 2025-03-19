"""Contains some shared types for properties"""

from collections.abc import MutableMapping
from http import HTTPStatus
from typing import Any, BinaryIO, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator

FileJsonType = tuple[Optional[str], BinaryIO, Optional[str]]


class File(BaseModel):
    """Contains information for file uploads"""

    model_config = ConfigDict(extra="allow")  # Removed arbitrary_types_allowed

    payload: Any  # BinaryIO
    file_name: Optional[str] = None
    mime_type: Optional[str] = None

    @field_validator("payload")
    @classmethod
    def validate_payload(cls, v: Any) -> Any:
        """Validate that payload is a binary file-like object"""
        # Check for essential BinaryIO methods
        required_attrs = ["read", "seek", "tell"]
        for attr in required_attrs:
            if not hasattr(v, attr):
                raise ValueError(
                    f"Payload must be a file-like object with '{attr}' method"
                )
        return v

    def to_tuple(self) -> FileJsonType:
        """Return a tuple representation that httpx will accept for multipart/form-data"""
        return self.file_name, self.payload, self.mime_type


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    """A response from an endpoint"""

    status_code: HTTPStatus
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[T]


__all__ = ["File", "FileJsonType", "Response"]
