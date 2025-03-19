from enum import Enum


class UploadAttachmentResponseSharingOption(str, Enum):
    ALLOWED = "Allowed"
    RESTRICTED = "Restricted"

    def __str__(self) -> str:
        return str(self.value)
