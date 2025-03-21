from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.get_report_response_attributes import GetReportResponseAttributes
from ..models.get_report_response_groupings_across import (
    GetReportResponseGroupingsAcross,
)
from ..models.get_report_response_groupings_down import GetReportResponseGroupingsDown
from ..models.get_report_response_report_metadata import GetReportResponseReportMetadata


class GetReportResponse(BaseModel):
    """
    Attributes:
        all_data (Optional[bool]): The All data Example: True.
        attributes (Optional[GetReportResponseAttributes]):
        groupings_across (Optional[GetReportResponseGroupingsAcross]):
        groupings_down (Optional[GetReportResponseGroupingsDown]):
        has_detail_rows (Optional[bool]): The Has detail rows Example: True.
        report_metadata (Optional[GetReportResponseReportMetadata]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    all_data: Optional[bool] = Field(alias="allData", default=None)
    attributes: Optional["GetReportResponseAttributes"] = Field(
        alias="attributes", default=None
    )
    groupings_across: Optional["GetReportResponseGroupingsAcross"] = Field(
        alias="groupingsAcross", default=None
    )
    groupings_down: Optional["GetReportResponseGroupingsDown"] = Field(
        alias="groupingsDown", default=None
    )
    has_detail_rows: Optional[bool] = Field(alias="hasDetailRows", default=None)
    report_metadata: Optional["GetReportResponseReportMetadata"] = Field(
        alias="reportMetadata", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetReportResponse"], src_dict: Dict[str, Any]):
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
