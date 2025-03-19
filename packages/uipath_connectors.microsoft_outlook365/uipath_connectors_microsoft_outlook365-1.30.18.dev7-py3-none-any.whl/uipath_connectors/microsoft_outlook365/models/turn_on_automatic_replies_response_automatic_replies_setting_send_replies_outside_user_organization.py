from enum import Enum


class TurnOnAutomaticRepliesResponseAutomaticRepliesSettingSendRepliesOutsideUserOrganization(
    str, Enum
):
    ALL = "all"
    CONTACTSONLY = "contactsOnly"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
