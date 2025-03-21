from enum import Enum


class CreateWorkbookRequestConflictBehavior(str, Enum):
    AUTO_RENAME = "rename"
    DONT_REPLACE = "fail"
    REPLACE = "replace"

    def __str__(self) -> str:
        return str(self.value)
