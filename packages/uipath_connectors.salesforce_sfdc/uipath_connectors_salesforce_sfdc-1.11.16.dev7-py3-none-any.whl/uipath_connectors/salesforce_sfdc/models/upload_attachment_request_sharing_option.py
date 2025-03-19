from enum import Enum


class UploadAttachmentRequestSharingOption(str, Enum):
    ALLOWED = "Allowed"
    RESTRICTED = "Restricted"

    def __str__(self) -> str:
        return str(self.value)
