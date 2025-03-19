from enum import Enum


class UpdateCalendarEventRequestEventSensitivityLevel(str, Enum):
    CONFIDENTIAL = "confidential"
    NORMAL = "normal"
    PERSONAL = "personal"
    PRIVATE = "private"

    def __str__(self) -> str:
        return str(self.value)
