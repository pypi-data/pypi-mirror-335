from enum import Enum


class FindUserByEmailAccountType(str, Enum):
    APP = "app"
    ATLASSIAN = "atlassian"
    CUSTOMER = "customer"
    UNKNOWN = "unknown"

    def __str__(self) -> str:
        return str(self.value)
