from enum import Enum


class ListCalendarEventsShowAs(str, Enum):
    BUSY = "busy"
    FREE = "free"
    OOF = "oof"
    TENTATIVE = "tentative"
    UNKNOWN = "unknown"
    WORKINGELSEWHERE = "workingElsewhere"

    def __str__(self) -> str:
        return str(self.value)
