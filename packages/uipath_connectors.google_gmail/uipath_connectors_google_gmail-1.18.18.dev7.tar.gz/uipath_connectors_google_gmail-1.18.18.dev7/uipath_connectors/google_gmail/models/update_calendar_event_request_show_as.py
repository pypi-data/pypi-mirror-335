from enum import Enum


class UpdateCalendarEventRequestShowAs(str, Enum):
    BUSY = "Busy"
    FREE = "Free"

    def __str__(self) -> str:
        return str(self.value)
