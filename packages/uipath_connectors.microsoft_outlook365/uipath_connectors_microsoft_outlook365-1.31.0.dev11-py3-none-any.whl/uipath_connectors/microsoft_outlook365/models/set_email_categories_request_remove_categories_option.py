from enum import Enum


class SetEmailCategoriesRequestRemoveCategoriesOption(str, Enum):
    ALL = "all"
    NONE = "none"
    SPECIFIC = "specific"

    def __str__(self) -> str:
        return str(self.value)
