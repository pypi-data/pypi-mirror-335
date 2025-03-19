from enum import Enum


class MarkEmailReadorUnreadRequestMarkAs(str, Enum):
    FALSE = "false"
    TRUE = "true"

    def __str__(self) -> str:
        return str(self.value)
