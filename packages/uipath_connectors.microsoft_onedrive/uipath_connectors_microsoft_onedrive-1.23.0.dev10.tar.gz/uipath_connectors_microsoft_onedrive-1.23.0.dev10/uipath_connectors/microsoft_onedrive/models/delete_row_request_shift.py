from enum import Enum


class DeleteRowRequestShift(str, Enum):
    CLEAR = "none"
    DELETE = "up"

    def __str__(self) -> str:
        return str(self.value)
