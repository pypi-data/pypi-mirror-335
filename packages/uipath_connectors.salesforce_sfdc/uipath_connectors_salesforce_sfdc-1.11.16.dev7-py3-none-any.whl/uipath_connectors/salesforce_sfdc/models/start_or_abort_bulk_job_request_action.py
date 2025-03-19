from enum import Enum


class StartOrAbortBulkJobRequestAction(str, Enum):
    ABORTED = "Aborted"
    UPLOADCOMPLETE = "UploadComplete"

    def __str__(self) -> str:
        return str(self.value)
