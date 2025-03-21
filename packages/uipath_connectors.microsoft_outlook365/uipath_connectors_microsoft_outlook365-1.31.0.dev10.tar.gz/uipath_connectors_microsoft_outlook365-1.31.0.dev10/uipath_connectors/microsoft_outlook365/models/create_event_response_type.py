from enum import Enum


class CreateEventResponseType(str, Enum):
    EXCEPTION = "exception"
    OCCURRENCE = "occurrence"
    SERIES_MASTER = "seriesMaster"
    SINGLE_INSTANCE = "singleInstance"

    def __str__(self) -> str:
        return str(self.value)
