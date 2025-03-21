from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.upload_attachment_response_attributes import (
    UploadAttachmentResponseAttributes,
)
from ..models.upload_attachment_response_content_location import (
    UploadAttachmentResponseContentLocation,
)
from ..models.upload_attachment_response_origin import UploadAttachmentResponseOrigin
from ..models.upload_attachment_response_sharing_option import (
    UploadAttachmentResponseSharingOption,
)
from ..models.upload_attachment_response_sharing_privacy import (
    UploadAttachmentResponseSharingPrivacy,
)
import datetime


class UploadAttachmentResponse(BaseModel):
    """
    Attributes:
        checksum (Optional[str]):  Example: 770884ac42a037209d644edf64843a84.
        content_body_id (Optional[str]):  Example: 05T5e00000l5V7zEAE.
        content_document_id (Optional[str]): The unique identifier for the uploaded file version Example:
                0695e00000BiqxgAAB.
        content_location (Optional[UploadAttachmentResponseContentLocation]):  Example: S.
        content_modified_by_id (Optional[str]):  Example: 0055e000003qrVYAAY.
        content_modified_date (Optional[datetime.datetime]):  Example: 2023-04-05T15:46:18+05:30.
        content_size (Optional[int]):  Example: 52596.0.
        created_by_id (Optional[str]):  Example: 0055e000003qrVYAAY.
        created_date (Optional[datetime.datetime]):  Example: 2023-04-05T15:46:18+05:30.
        file_extension (Optional[str]):  Example: png:image/png.
        file_type (Optional[str]):  Example: UNKNOWN.
        first_publish_location_id (Optional[str]):  Example: 0055e000003qrVYAAY.
        id (Optional[str]):  Example: 0685e00000C0CxTAAV.
        is_asset_enabled (Optional[bool]):
        is_deleted (Optional[bool]):
        is_latest (Optional[bool]):  Example: True.
        is_major_version (Optional[bool]):  Example: True.
        last_modified_by_id (Optional[str]):  Example: 0055e000003qrVYAAY.
        last_modified_date (Optional[datetime.datetime]):  Example: 2023-04-05T15:46:18+05:30.
        negative_rating_count (Optional[int]):
        origin (Optional[UploadAttachmentResponseOrigin]):  Example: C.
        owner_id (Optional[str]):  Example: 0055e000003qrVYAAY.
        path_on_client (Optional[str]): Name of the file Example: Capture.PNG:image/png.
        positive_rating_count (Optional[int]):
        publish_status (Optional[str]):  Example: R.
        rating_count (Optional[int]):
        sharing_option (Optional[UploadAttachmentResponseSharingOption]):  Example: A.
        sharing_privacy (Optional[UploadAttachmentResponseSharingPrivacy]):  Example: N.
        system_modstamp (Optional[datetime.datetime]):  Example: 2023-04-05T15:46:20+05:30.
        title (Optional[str]): The title of the file. Name of the file will be considered as default if no value is
                passed Example: Capture.PNG:image/png.
        version_data (Optional[str]):  Example:
                /services/data/v57.0/sobjects/ContentVersion/0685e00000C0CxTAAV/VersionData.
        version_data_url (Optional[str]):  Example: https://cloud-elementscom4-dev-
                ed.file.force.com/sfc/servlet.shepherd/version/download/0685e00000C0CxT.
        version_number (Optional[str]):  Example: 1.
        attributes (Optional[UploadAttachmentResponseAttributes]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    checksum: Optional[str] = Field(alias="Checksum", default=None)
    content_body_id: Optional[str] = Field(alias="ContentBodyId", default=None)
    content_document_id: Optional[str] = Field(alias="ContentDocumentId", default=None)
    content_location: Optional["UploadAttachmentResponseContentLocation"] = Field(
        alias="ContentLocation", default=None
    )
    content_modified_by_id: Optional[str] = Field(
        alias="ContentModifiedById", default=None
    )
    content_modified_date: Optional[datetime.datetime] = Field(
        alias="ContentModifiedDate", default=None
    )
    content_size: Optional[int] = Field(alias="ContentSize", default=None)
    created_by_id: Optional[str] = Field(alias="CreatedById", default=None)
    created_date: Optional[datetime.datetime] = Field(alias="CreatedDate", default=None)
    file_extension: Optional[str] = Field(alias="FileExtension", default=None)
    file_type: Optional[str] = Field(alias="FileType", default=None)
    first_publish_location_id: Optional[str] = Field(
        alias="FirstPublishLocationId", default=None
    )
    id: Optional[str] = Field(alias="Id", default=None)
    is_asset_enabled: Optional[bool] = Field(alias="IsAssetEnabled", default=None)
    is_deleted: Optional[bool] = Field(alias="IsDeleted", default=None)
    is_latest: Optional[bool] = Field(alias="IsLatest", default=None)
    is_major_version: Optional[bool] = Field(alias="IsMajorVersion", default=None)
    last_modified_by_id: Optional[str] = Field(alias="LastModifiedById", default=None)
    last_modified_date: Optional[datetime.datetime] = Field(
        alias="LastModifiedDate", default=None
    )
    negative_rating_count: Optional[int] = Field(
        alias="NegativeRatingCount", default=None
    )
    origin: Optional["UploadAttachmentResponseOrigin"] = Field(
        alias="Origin", default=None
    )
    owner_id: Optional[str] = Field(alias="OwnerId", default=None)
    path_on_client: Optional[str] = Field(alias="PathOnClient", default=None)
    positive_rating_count: Optional[int] = Field(
        alias="PositiveRatingCount", default=None
    )
    publish_status: Optional[str] = Field(alias="PublishStatus", default=None)
    rating_count: Optional[int] = Field(alias="RatingCount", default=None)
    sharing_option: Optional["UploadAttachmentResponseSharingOption"] = Field(
        alias="SharingOption", default=None
    )
    sharing_privacy: Optional["UploadAttachmentResponseSharingPrivacy"] = Field(
        alias="SharingPrivacy", default=None
    )
    system_modstamp: Optional[datetime.datetime] = Field(
        alias="SystemModstamp", default=None
    )
    title: Optional[str] = Field(alias="Title", default=None)
    version_data: Optional[str] = Field(alias="VersionData", default=None)
    version_data_url: Optional[str] = Field(alias="VersionDataUrl", default=None)
    version_number: Optional[str] = Field(alias="VersionNumber", default=None)
    attributes: Optional["UploadAttachmentResponseAttributes"] = Field(
        alias="attributes", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UploadAttachmentResponse"], src_dict: Dict[str, Any]):
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
