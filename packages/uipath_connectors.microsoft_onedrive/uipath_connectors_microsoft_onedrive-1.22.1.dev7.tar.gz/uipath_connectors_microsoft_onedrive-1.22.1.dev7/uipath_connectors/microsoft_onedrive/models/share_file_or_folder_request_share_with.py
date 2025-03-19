from enum import Enum


class ShareFileOrFolderRequestShareWith(str, Enum):
    ANONYMOUS = "anonymous"
    ORGANIZATION = "organization"

    def __str__(self) -> str:
        return str(self.value)
