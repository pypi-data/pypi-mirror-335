from enum import Enum


class UpdateEventResponseShowAs(str, Enum):
    AWAY_OUT_OF_OFFICE = "oof"
    BUSY = "busy"
    FREE = "free"
    TENTATIVE = "tentative"
    WORKING_ELSEWHERE = "workingElsewhere"

    def __str__(self) -> str:
        return str(self.value)
