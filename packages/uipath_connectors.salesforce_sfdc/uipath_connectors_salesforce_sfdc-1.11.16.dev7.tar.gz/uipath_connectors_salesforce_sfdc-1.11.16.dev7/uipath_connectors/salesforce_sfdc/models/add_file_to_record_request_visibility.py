from enum import Enum


class AddFileToRecordRequestVisibility(str, Enum):
    ALLUSERS = "AllUsers"
    INTERNALUSERS = "InternalUsers"
    SHAREDUSERS = "SharedUsers"

    def __str__(self) -> str:
        return str(self.value)
