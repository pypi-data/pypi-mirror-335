from enum import Enum


class UploadAttachmentResponseOrigin(str, Enum):
    C = "C"
    H = "H"

    def __str__(self) -> str:
        return str(self.value)
