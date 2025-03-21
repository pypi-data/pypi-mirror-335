from enum import Enum


class UpdateEventRequestChangeResourceAttendees(str, Enum):
    ADD_ANDOR_REMOVE = "addRemove"
    NO_CHANGE = "noChange"
    OVERWRITE = "overwrite"

    def __str__(self) -> str:
        return str(self.value)
