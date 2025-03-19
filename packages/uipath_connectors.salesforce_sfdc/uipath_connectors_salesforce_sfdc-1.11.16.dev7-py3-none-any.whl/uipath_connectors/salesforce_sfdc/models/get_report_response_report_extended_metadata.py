from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_report_response_report_extended_metadata_report_extended_metadata_aggregate_column_info import (
    GetReportResponseReportExtendedMetadataReportExtendedMetadataAggregateColumnInfo,
)
from ..models.get_report_response_report_extended_metadata_report_extended_metadata_detail_column_info import (
    GetReportResponseReportExtendedMetadataReportExtendedMetadataDetailColumnInfo,
)
from ..models.get_report_response_report_extended_metadata_report_extended_metadata_grouping_column_info import (
    GetReportResponseReportExtendedMetadataReportExtendedMetadataGroupingColumnInfo,
)


class GetReportResponseReportExtendedMetadata(BaseModel):
    """
    Attributes:
        aggregate_column_info
                (Optional[GetReportResponseReportExtendedMetadataReportExtendedMetadataAggregateColumnInfo]): The Report
                extended metadata aggregate column info
        detail_column_info (Optional[GetReportResponseReportExtendedMetadataReportExtendedMetadataDetailColumnInfo]):
                The Report extended metadata detail column info
        grouping_column_info
                (Optional[GetReportResponseReportExtendedMetadataReportExtendedMetadataGroupingColumnInfo]): The Report extended
                metadata grouping column info
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    aggregate_column_info: Optional[
        "GetReportResponseReportExtendedMetadataReportExtendedMetadataAggregateColumnInfo"
    ] = Field(alias="aggregateColumnInfo", default=None)
    detail_column_info: Optional[
        "GetReportResponseReportExtendedMetadataReportExtendedMetadataDetailColumnInfo"
    ] = Field(alias="detailColumnInfo", default=None)
    grouping_column_info: Optional[
        "GetReportResponseReportExtendedMetadataReportExtendedMetadataGroupingColumnInfo"
    ] = Field(alias="groupingColumnInfo", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetReportResponseReportExtendedMetadata"], src_dict: Dict[str, Any]
    ):
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
