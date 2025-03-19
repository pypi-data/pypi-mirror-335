from enum import Enum


class ListCalendarEventsAttendeesArrayItemRefAttendeeType(str, Enum):
    OPTIONAL = "optional"
    REQUIRED = "required"
    RESOURCE = "resource"

    def __str__(self) -> str:
        return str(self.value)
