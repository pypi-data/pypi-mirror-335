from enum import Enum


class CreateShareLinkRequestScope(str, Enum):
    ANONYMOUS = "anonymous"
    ORGANIZATION = "organization"
    USERS = "users"

    def __str__(self) -> str:
        return str(self.value)
