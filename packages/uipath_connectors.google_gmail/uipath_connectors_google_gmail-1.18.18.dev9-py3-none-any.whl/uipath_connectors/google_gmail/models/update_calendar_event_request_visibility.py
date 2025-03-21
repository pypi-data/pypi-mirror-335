from enum import Enum


class UpdateCalendarEventRequestVisibility(str, Enum):
    CONFIDENTIAL = "confidential"
    DEFAULT = "default"
    PRIVATE = "private"
    PUBLIC = "public"

    def __str__(self) -> str:
        return str(self.value)
