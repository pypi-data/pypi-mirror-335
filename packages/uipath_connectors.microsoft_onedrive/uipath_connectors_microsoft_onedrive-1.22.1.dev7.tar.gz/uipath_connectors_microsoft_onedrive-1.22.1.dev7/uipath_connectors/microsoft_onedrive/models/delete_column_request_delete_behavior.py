from enum import Enum


class DeleteColumnRequestDeleteBehavior(str, Enum):
    LEFT = "left"
    NONE = "none"

    def __str__(self) -> str:
        return str(self.value)
