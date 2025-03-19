from enum import Enum


class TurnOnAutomaticRepliesRequestAutomaticRepliesSettingSendRepliesOutsideUserOrganization(
    str, Enum
):
    ALL = "all"
    CONTACTSONLY = "contactsOnly"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
