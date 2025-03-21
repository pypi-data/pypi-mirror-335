from enum import Enum


class CreateShareLinkRequestType(str, Enum):
    EDIT = "edit"
    EMBED = "embed"
    VIEW = "view"

    def __str__(self) -> str:
        return str(self.value)
