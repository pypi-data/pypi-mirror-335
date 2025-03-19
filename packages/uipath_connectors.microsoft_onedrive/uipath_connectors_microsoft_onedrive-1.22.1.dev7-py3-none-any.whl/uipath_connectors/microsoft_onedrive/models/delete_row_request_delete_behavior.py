from enum import Enum


class DeleteRowRequestDeleteBehavior(str, Enum):
    NONE = "none"
    UP = "up"

    def __str__(self) -> str:
        return str(self.value)
