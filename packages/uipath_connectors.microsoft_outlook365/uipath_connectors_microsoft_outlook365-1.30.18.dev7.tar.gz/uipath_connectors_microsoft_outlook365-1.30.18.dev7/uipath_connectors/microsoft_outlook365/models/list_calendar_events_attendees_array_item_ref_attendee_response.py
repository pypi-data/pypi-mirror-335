from enum import Enum


class ListCalendarEventsAttendeesArrayItemRefAttendeeResponse(str, Enum):
    ACCEPTED = "accepted"
    DECLINED = "declined"
    NONE = "none"
    NOTRESPONDED = "notResponded"
    ORGANIZER = "organizer"
    TENTATIVELYACCEPTED = "tentativelyAccepted"

    def __str__(self) -> str:
        return str(self.value)
