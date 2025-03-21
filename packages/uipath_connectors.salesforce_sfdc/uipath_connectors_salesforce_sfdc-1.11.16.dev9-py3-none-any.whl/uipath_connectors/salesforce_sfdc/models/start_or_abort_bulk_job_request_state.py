from enum import Enum


class StartOrAbortBulkJobRequestState(str, Enum):
    ABORT = "Aborted"
    START = "UploadComplete"

    def __str__(self) -> str:
        return str(self.value)
