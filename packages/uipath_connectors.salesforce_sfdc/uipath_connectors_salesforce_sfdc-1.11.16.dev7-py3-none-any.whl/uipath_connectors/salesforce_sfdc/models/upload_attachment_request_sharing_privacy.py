from enum import Enum


class UploadAttachmentRequestSharingPrivacy(str, Enum):
    N = "N"
    P = "P"

    def __str__(self) -> str:
        return str(self.value)
