from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.add_file_to_record_request_share_type import (
    AddFileToRecordRequestShareType,
)
from ..models.add_file_to_record_request_visibility import (
    AddFileToRecordRequestVisibility,
)


class AddFileToRecordRequest(BaseModel):
    """
    Attributes:
        content_document_id (str): Pass the file ID from the output of “Upload File” or “Search Records → Content
                Document” activity Example: 0695e00000AL84GAAT.
        linked_entity_id (str): Pass the ID of the linked object such as Account, Opportunity, Account etc. ID can also
                be retrieved from the event trigger output or “Search Records” Example: 0015e00000AeuOBAAZ.
        share_type (AddFileToRecordRequestShareType): The permission granted to the user of the shared file in a library
                Example: C.
        visibility (Optional[AddFileToRecordRequestVisibility]): Whether this file is available for all users, internal
                users or shared users? Default is all users Example: AllUsers.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content_document_id: str = Field(alias="ContentDocumentId")
    linked_entity_id: str = Field(alias="LinkedEntityId")
    share_type: "AddFileToRecordRequestShareType" = Field(alias="ShareType")
    visibility: Optional["AddFileToRecordRequestVisibility"] = Field(
        alias="Visibility", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["AddFileToRecordRequest"], src_dict: Dict[str, Any]):
        return cls.model_validate(src_dict)

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
