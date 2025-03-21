from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetReportResponseAttributes(BaseModel):
    """
    Attributes:
        describe_url (Optional[str]): The Attributes describe url Example:
                /services/data/v35.0/analytics/reports/00OR0000000K2UeMAK/describe.
        instances_url (Optional[str]): The Attributes instances url Example:
                /services/data/v35.0/analytics/reports/00OR0000000K2UeMAK/instances.
        report_id (Optional[str]): The Attributes report ID Example: 00OR0000000K2UeMAK.
        report_name (Optional[str]): The Attributes report name Example: Deals Closing This Quarter.
        type_ (Optional[str]): The Attributes type Example: Report.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    describe_url: Optional[str] = Field(alias="describeUrl", default=None)
    instances_url: Optional[str] = Field(alias="instancesUrl", default=None)
    report_id: Optional[str] = Field(alias="reportId", default=None)
    report_name: Optional[str] = Field(alias="reportName", default=None)
    type_: Optional[str] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetReportResponseAttributes"], src_dict: Dict[str, Any]):
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
