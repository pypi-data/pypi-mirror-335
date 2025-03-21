from enum import Enum


class CreateEventRequestShowAs(str, Enum):
    BUSY = "busy"
    FREE = "free"
    OOF = "oof"
    TENTATIVE = "tentative"
    UNKNOWN = "unknown"
    WORKING_ELSEWHERE = "workingElsewhere"

    def __str__(self) -> str:
        return str(self.value)
