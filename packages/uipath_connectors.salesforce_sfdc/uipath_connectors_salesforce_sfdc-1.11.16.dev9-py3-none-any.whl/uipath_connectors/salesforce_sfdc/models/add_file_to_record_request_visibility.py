from enum import Enum


class AddFileToRecordRequestVisibility(str, Enum):
    ALL_USERS = "AllUsers"
    INTERNAL_USERS = "InternalUsers"
    SHARED_USERS = "SharedUsers"

    def __str__(self) -> str:
        return str(self.value)
