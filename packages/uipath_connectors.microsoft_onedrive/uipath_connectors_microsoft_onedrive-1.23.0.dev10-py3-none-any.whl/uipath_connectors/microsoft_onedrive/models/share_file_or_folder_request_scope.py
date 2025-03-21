from enum import Enum


class ShareFileOrFolderRequestScope(str, Enum):
    ANYONE = "anonymous"
    ORGANIZATION = "organization"

    def __str__(self) -> str:
        return str(self.value)
