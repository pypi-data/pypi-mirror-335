from enum import Enum


class UploadAttachmentResponseContentLocation(str, Enum):
    E = "E"
    L = "L"
    S = "S"

    def __str__(self) -> str:
        return str(self.value)
