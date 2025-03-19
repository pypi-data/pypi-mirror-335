from enum import Enum


class CreateCalendarEventResponseEventType(str, Enum):
    EXCEPTION = "exception"
    OCCURRENCE = "occurrence"
    SERIESMASTER = "seriesMaster"
    SINGLEINSTANCE = "singleInstance"

    def __str__(self) -> str:
        return str(self.value)
