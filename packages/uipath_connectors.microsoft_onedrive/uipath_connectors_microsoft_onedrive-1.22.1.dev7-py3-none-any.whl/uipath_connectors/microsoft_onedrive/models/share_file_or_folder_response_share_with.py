from enum import Enum


class ShareFileOrFolderResponseShareWith(str, Enum):
    ANONYMOUS = "anonymous"
    ORGANIZATION = "organization"

    def __str__(self) -> str:
        return str(self.value)
