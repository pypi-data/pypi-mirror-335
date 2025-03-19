from enum import Enum


class CreateCalendarEventRequestShowAs(str, Enum):
    BUSY = "Busy"
    FREE = "Free"

    def __str__(self) -> str:
        return str(self.value)
