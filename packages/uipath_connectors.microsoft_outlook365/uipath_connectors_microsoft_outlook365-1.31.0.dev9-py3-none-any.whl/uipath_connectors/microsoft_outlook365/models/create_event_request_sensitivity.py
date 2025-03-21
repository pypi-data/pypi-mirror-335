from enum import Enum


class CreateEventRequestSensitivity(str, Enum):
    CONFIDENTIAL = "confidential"
    NORMAL = "normal"
    PERSONAL = "personal"
    PRIVATE = "private"

    def __str__(self) -> str:
        return str(self.value)
