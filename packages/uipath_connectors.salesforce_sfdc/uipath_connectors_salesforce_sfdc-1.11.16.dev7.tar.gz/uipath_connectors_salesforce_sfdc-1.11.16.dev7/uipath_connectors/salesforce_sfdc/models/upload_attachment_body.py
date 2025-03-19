import json
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..types import File
from ..models.upload_attachment_request import UploadAttachmentRequest


class UploadAttachmentBody(BaseModel):
    """
    Attributes:
        file (File): attachments to be uploaded
        body (Optional[UploadAttachmentRequest]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    file: File = Field(alias="file")
    body: Optional["UploadAttachmentRequest"] = Field(alias="body", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UploadAttachmentBody"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

    def to_multipart(self) -> dict[str, Any]:
        file = self.file.to_tuple()

        body: Optional[tuple[None, bytes, str]] = None
        if self.body is not None:
            body = (None, json.dumps(self.body.to_dict()).encode(), "application/json")
        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_keys:
            field_dict[prop_name] = (
                None,
                str(self.__getitem__(prop)).encode(),
                "text/plain",
            )
        field_dict.update(
            {
                "file": file,
            }
        )
        if body is not None:
            field_dict["body"] = body

        return field_dict

    @property
    def additional_keys(self) -> list[str]:
        base_fields = self.model_fields.keys()
        return [k for k in self.__dict__ if k not in base_fields]

    def __getitem__(self, key: str) -> Any:
        if key in self.__dict__:
            return self.__dict__[key]
        raise KeyError(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__dict__[key] = value

    def __delitem__(self, key: str) -> None:
        if key in self.__dict__:
            del self.__dict__[key]
        else:
            raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__
