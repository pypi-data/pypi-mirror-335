from enum import Enum


class UploadAttachmentResponseSharingPrivacy(str, Enum):
    N = "N"
    P = "P"

    def __str__(self) -> str:
        return str(self.value)
