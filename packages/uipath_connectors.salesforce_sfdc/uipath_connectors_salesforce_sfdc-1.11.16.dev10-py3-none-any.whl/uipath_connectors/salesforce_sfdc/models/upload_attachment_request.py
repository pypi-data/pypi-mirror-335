from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.upload_attachment_request_content_location import (
    UploadAttachmentRequestContentLocation,
)
from ..models.upload_attachment_request_origin import UploadAttachmentRequestOrigin
from ..models.upload_attachment_request_sharing_option import (
    UploadAttachmentRequestSharingOption,
)
from ..models.upload_attachment_request_sharing_privacy import (
    UploadAttachmentRequestSharingPrivacy,
)
import datetime


class UploadAttachmentRequest(BaseModel):
    """
    Attributes:
        content_body_id (Optional[str]):  Example: 05T5e00000l5V7zEAE.
        content_document_id (Optional[str]): The unique identifier for the uploaded file version Example:
                0695e00000BiqxgAAB.
        content_location (Optional[UploadAttachmentRequestContentLocation]):  Example: S.
        content_modified_date (Optional[datetime.datetime]):  Example: 2023-04-05T15:46:18+05:30.
        content_url (Optional[str]):  Example: urlString.
        description (Optional[str]): Description of the file version Example: some desc.
        external_data_source_id (Optional[str]):
        external_document_info_1 (Optional[str]):  Example: URL.
        external_document_info_2 (Optional[str]):  Example: external file ID.
        first_publish_location_id (Optional[str]):  Example: 0055e000003qrVYAAY.
        is_asset_enabled (Optional[bool]):
        is_major_version (Optional[bool]):  Example: True.
        origin (Optional[UploadAttachmentRequestOrigin]):  Example: C.
        owner_id (Optional[str]):  Example: 0055e000003qrVYAAY.
        path_on_client (Optional[str]): Name of the file Example: Capture.PNG:image/png.
        reason_for_change (Optional[str]):  Example: Reason.
        sharing_option (Optional[UploadAttachmentRequestSharingOption]):  Example: A.
        sharing_privacy (Optional[UploadAttachmentRequestSharingPrivacy]):  Example: N.
        tag_csv (Optional[str]):  Example: tags.
        title (Optional[str]): The title of the file. Name of the file will be considered as default if no value is
                passed Example: Capture.PNG:image/png.
        version_data (Optional[str]):  Example:
                /services/data/v57.0/sobjects/ContentVersion/0685e00000C0CxTAAV/VersionData.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    content_body_id: Optional[str] = Field(alias="ContentBodyId", default=None)
    content_document_id: Optional[str] = Field(alias="ContentDocumentId", default=None)
    content_location: Optional["UploadAttachmentRequestContentLocation"] = Field(
        alias="ContentLocation", default=None
    )
    content_modified_date: Optional[datetime.datetime] = Field(
        alias="ContentModifiedDate", default=None
    )
    content_url: Optional[str] = Field(alias="ContentUrl", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    external_data_source_id: Optional[str] = Field(
        alias="ExternalDataSourceId", default=None
    )
    external_document_info_1: Optional[str] = Field(
        alias="ExternalDocumentInfo1", default=None
    )
    external_document_info_2: Optional[str] = Field(
        alias="ExternalDocumentInfo2", default=None
    )
    first_publish_location_id: Optional[str] = Field(
        alias="FirstPublishLocationId", default=None
    )
    is_asset_enabled: Optional[bool] = Field(alias="IsAssetEnabled", default=None)
    is_major_version: Optional[bool] = Field(alias="IsMajorVersion", default=None)
    origin: Optional["UploadAttachmentRequestOrigin"] = Field(
        alias="Origin", default=None
    )
    owner_id: Optional[str] = Field(alias="OwnerId", default=None)
    path_on_client: Optional[str] = Field(alias="PathOnClient", default=None)
    reason_for_change: Optional[str] = Field(alias="ReasonForChange", default=None)
    sharing_option: Optional["UploadAttachmentRequestSharingOption"] = Field(
        alias="SharingOption", default=None
    )
    sharing_privacy: Optional["UploadAttachmentRequestSharingPrivacy"] = Field(
        alias="SharingPrivacy", default=None
    )
    tag_csv: Optional[str] = Field(alias="TagCsv", default=None)
    title: Optional[str] = Field(alias="Title", default=None)
    version_data: Optional[str] = Field(alias="VersionData", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UploadAttachmentRequest"], src_dict: Dict[str, Any]):
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
