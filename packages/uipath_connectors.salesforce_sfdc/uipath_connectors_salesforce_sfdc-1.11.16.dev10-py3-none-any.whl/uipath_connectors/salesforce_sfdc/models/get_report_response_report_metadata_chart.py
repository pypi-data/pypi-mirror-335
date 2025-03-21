from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetReportResponseReportMetadataChart(BaseModel):
    """
    Attributes:
        chart_type (Optional[str]): The Report metadata chart type Example: Donut.
        groupings (Optional[list[str]]):
        has_legend (Optional[bool]): The Report metadata chart has legend Example: True.
        show_chart_values (Optional[bool]): The Report metadata chart show chart values
        summaries (Optional[list[str]]):
        summary_axis_locations (Optional[list[str]]):
        title (Optional[str]): The Report metadata chart title Example: Pipeline by Stage and Type.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    chart_type: Optional[str] = Field(alias="chartType", default=None)
    groupings: Optional[list[str]] = Field(alias="groupings", default=None)
    has_legend: Optional[bool] = Field(alias="hasLegend", default=None)
    show_chart_values: Optional[bool] = Field(alias="showChartValues", default=None)
    summaries: Optional[list[str]] = Field(alias="summaries", default=None)
    summary_axis_locations: Optional[list[str]] = Field(
        alias="summaryAxisLocations", default=None
    )
    title: Optional[str] = Field(alias="title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["GetReportResponseReportMetadataChart"], src_dict: Dict[str, Any]
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
