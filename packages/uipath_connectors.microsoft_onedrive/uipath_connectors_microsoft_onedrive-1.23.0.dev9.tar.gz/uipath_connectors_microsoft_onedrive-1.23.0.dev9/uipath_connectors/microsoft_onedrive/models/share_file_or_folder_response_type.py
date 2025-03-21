from enum import Enum


class ShareFileOrFolderResponseType(str, Enum):
    EDIT = "edit"
    VIEW = "view"

    def __str__(self) -> str:
        return str(self.value)
