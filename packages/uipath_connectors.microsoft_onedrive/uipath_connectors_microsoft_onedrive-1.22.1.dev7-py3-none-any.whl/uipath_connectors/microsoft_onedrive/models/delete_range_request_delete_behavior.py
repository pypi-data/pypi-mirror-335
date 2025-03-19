from enum import Enum


class DeleteRangeRequestDeleteBehavior(str, Enum):
    LEFT = "Left"
    NONE = "None"
    UP = "Up"

    def __str__(self) -> str:
        return str(self.value)
