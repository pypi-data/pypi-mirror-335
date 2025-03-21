from enum import Enum


class MarkEmailReadorUnreadRequestIsRead(str, Enum):
    READ = "true"
    UNREAD = "false"

    def __str__(self) -> str:
        return str(self.value)
