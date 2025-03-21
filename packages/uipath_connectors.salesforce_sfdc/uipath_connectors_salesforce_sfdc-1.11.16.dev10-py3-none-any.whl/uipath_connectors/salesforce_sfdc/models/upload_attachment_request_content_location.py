from enum import Enum


class UploadAttachmentRequestContentLocation(str, Enum):
    E = "E"
    L = "L"
    S = "S"

    def __str__(self) -> str:
        return str(self.value)
