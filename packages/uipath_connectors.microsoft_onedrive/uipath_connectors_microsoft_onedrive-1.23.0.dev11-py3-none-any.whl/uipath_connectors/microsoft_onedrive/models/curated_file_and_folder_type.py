from enum import Enum


class CuratedFileAndFolderType(str, Enum):
    FILE = "file"
    FOLDER = "folder"

    def __str__(self) -> str:
        return str(self.value)
