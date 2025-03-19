from enum import Enum


class UpdateCalendarEventResponseEventType(str, Enum):
    EXCEPTION = "exception"
    OCCURRENCE = "occurrence"
    SERIESMASTER = "seriesMaster"
    SINGLEINSTANCE = "singleInstance"

    def __str__(self) -> str:
        return str(self.value)
