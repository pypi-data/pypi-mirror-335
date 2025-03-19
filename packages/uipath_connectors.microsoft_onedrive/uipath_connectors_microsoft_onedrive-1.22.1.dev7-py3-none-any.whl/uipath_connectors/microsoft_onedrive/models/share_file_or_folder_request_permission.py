from enum import Enum


class ShareFileOrFolderRequestPermission(str, Enum):
    EDIT = "edit"
    VIEW = "view"

    def __str__(self) -> str:
        return str(self.value)
