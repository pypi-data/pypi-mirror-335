from enum import Enum


class ParameterizedSearchRequestIn(str, Enum):
    ALL = "ALL"
    EMAIL = "EMAIL"
    NAME = "NAME"
    PHONE = "PHONE"
    SIDEBAR = "SIDEBAR"

    def __str__(self) -> str:
        return str(self.value)
