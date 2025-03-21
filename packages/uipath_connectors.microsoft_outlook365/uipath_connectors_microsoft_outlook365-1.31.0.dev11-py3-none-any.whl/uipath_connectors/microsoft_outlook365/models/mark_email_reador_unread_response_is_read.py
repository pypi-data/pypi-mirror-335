from enum import Enum


class MarkEmailReadorUnreadResponseIsRead(str, Enum):
    READ = "true"
    UNREAD = "false"

    def __str__(self) -> str:
        return str(self.value)
