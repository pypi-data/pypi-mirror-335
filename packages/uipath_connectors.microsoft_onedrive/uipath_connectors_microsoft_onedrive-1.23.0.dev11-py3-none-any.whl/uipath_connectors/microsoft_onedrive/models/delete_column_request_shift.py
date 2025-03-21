from enum import Enum


class DeleteColumnRequestShift(str, Enum):
    CLEAR_CONTENT = "none"
    DELETE = "left"

    def __str__(self) -> str:
        return str(self.value)
