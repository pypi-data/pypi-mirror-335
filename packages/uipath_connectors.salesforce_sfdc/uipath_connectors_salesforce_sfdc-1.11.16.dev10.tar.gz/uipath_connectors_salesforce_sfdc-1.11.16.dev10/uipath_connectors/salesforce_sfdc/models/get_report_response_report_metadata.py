from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_report_response_report_metadata_chart import (
    GetReportResponseReportMetadataChart,
)
from ..models.get_report_response_report_metadata_report_type import (
    GetReportResponseReportMetadataReportType,
)
from ..models.get_report_response_report_metadata_standard_date_filter import (
    GetReportResponseReportMetadataStandardDateFilter,
)
from ..models.get_report_response_report_metadata_standard_filters_array_item_ref import (
    GetReportResponseReportMetadataStandardFiltersArrayItemRef,
)


class GetReportResponseReportMetadata(BaseModel):
    """
    Attributes:
        aggregates (Optional[list[str]]):
        chart (Optional[GetReportResponseReportMetadataChart]):
        detail_columns (Optional[list[str]]):
        developer_name (Optional[str]): The Report metadata developer name Example: Deals_Closing_This_Quarter.
        folder_id (Optional[str]): The Report metadata folder ID Example: 00lR0000000M8IiIAK.
        groupings_across (Optional[list[Any]]): The Report metadata groupings across
        has_detail_rows (Optional[bool]): The Report metadata has detail rows Example: True.
        has_record_count (Optional[bool]): The Report metadata has record count Example: True.
        historical_snapshot_dates (Optional[list[Any]]): The Report metadata historical snapshot dates
        id (Optional[str]): The Report metadata ID Example: 00OR0000000K2UeMAK.
        name (Optional[str]): The Report metadata name Example: Deals Closing This Quarter.
        report_filters (Optional[list[Any]]): The Report metadata report filters
        report_format (Optional[str]): The Report metadata report format Example: MATRIX.
        report_type (Optional[GetReportResponseReportMetadataReportType]):
        scope (Optional[str]): The Report metadata scope Example: organization.
        show_grand_total (Optional[bool]): The Report metadata show grand total Example: True.
        show_subtotals (Optional[bool]): The Report metadata show subtotals Example: True.
        sort_by (Optional[list[Any]]): The Report metadata sort by
        standard_date_filter (Optional[GetReportResponseReportMetadataStandardDateFilter]):
        standard_filters (Optional[list['GetReportResponseReportMetadataStandardFiltersArrayItemRef']]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    aggregates: Optional[list[str]] = Field(alias="aggregates", default=None)
    chart: Optional["GetReportResponseReportMetadataChart"] = Field(
        alias="chart", default=None
    )
    detail_columns: Optional[list[str]] = Field(alias="detailColumns", default=None)
    developer_name: Optional[str] = Field(alias="developerName", default=None)
    folder_id: Optional[str] = Field(alias="folderId", default=None)
    groupings_across: Optional[list[Any]] = Field(alias="groupingsAcross", default=None)
    has_detail_rows: Optional[bool] = Field(alias="hasDetailRows", default=None)
    has_record_count: Optional[bool] = Field(alias="hasRecordCount", default=None)
    historical_snapshot_dates: Optional[list[Any]] = Field(
        alias="historicalSnapshotDates", default=None
    )
    id: Optional[str] = Field(alias="id", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    report_filters: Optional[list[Any]] = Field(alias="reportFilters", default=None)
    report_format: Optional[str] = Field(alias="reportFormat", default=None)
    report_type: Optional["GetReportResponseReportMetadataReportType"] = Field(
        alias="reportType", default=None
    )
    scope: Optional[str] = Field(alias="scope", default=None)
    show_grand_total: Optional[bool] = Field(alias="showGrandTotal", default=None)
    show_subtotals: Optional[bool] = Field(alias="showSubtotals", default=None)
    sort_by: Optional[list[Any]] = Field(alias="sortBy", default=None)
    standard_date_filter: Optional[
        "GetReportResponseReportMetadataStandardDateFilter"
    ] = Field(alias="standardDateFilter", default=None)
    standard_filters: Optional[
        list["GetReportResponseReportMetadataStandardFiltersArrayItemRef"]
    ] = Field(alias="standardFilters", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetReportResponseReportMetadata"], src_dict: Dict[str, Any]
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
