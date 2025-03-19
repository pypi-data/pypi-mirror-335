from enum import Enum


class GetCommentsVisibilityVisibilityType(str, Enum):
    GROUP = "group"
    ROLE = "role"

    def __str__(self) -> str:
        return str(self.value)
