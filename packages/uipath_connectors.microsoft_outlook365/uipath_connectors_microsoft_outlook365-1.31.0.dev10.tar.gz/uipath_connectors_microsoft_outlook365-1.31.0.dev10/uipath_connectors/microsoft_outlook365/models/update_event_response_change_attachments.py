from enum import Enum


class UpdateEventResponseChangeAttachments(str, Enum):
    ADD_ANDOR_REMOVE = "addRemove"
    NO_CHANGE = "noChange"
    OVERWRITE = "owerwrite"

    def __str__(self) -> str:
        return str(self.value)
