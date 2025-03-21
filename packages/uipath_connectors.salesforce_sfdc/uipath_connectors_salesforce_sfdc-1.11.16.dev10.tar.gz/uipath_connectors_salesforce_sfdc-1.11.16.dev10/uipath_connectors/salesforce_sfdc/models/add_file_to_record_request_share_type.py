from enum import Enum


class AddFileToRecordRequestShareType(str, Enum):
    COLLABORATOR_PERMISSION = "Collaborator Permission"
    INFERRED_PERMISSION = "Inferred Permission"
    VIEWER_PERMISSION = "Viewer Permission"

    def __str__(self) -> str:
        return str(self.value)
