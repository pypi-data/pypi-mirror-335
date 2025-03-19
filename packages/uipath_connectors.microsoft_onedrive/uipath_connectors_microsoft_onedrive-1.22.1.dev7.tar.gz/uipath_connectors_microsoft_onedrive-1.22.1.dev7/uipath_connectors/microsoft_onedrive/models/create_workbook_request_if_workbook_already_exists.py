from enum import Enum


class CreateWorkbookRequestIfWorkbookAlreadyExists(str, Enum):
    FAIL = "fail"
    RENAME = "rename"
    REPLACE = "replace"

    def __str__(self) -> str:
        return str(self.value)
