from enum import Enum


class ListEmailType(str, Enum):
    EMAIL = "email"

    def __str__(self) -> str:
        return str(self.value)
