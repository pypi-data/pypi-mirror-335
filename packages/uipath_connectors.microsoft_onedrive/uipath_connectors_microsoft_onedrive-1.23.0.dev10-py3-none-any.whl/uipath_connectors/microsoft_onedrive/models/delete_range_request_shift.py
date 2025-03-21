from enum import Enum


class DeleteRangeRequestShift(str, Enum):
    CLEAR = "None"
    COLUMN = "Left"
    ROWS = "Up"

    def __str__(self) -> str:
        return str(self.value)
