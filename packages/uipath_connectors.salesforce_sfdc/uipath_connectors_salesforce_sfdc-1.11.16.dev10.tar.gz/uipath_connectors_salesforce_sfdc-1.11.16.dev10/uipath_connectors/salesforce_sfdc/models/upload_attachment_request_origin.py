from enum import Enum


class UploadAttachmentRequestOrigin(str, Enum):
    C = "C"
    H = "H"

    def __str__(self) -> str:
        return str(self.value)
