from enum import Enum


class ListCalendarEventsSensitivity(str, Enum):
    CONFIDENTIAL = "confidential"
    NORMAL = "normal"
    PERSONAL = "personal"
    PRIVATE = "private"

    def __str__(self) -> str:
        return str(self.value)
