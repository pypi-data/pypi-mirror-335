from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class GetBulkUploadJobInfoResponse(BaseModel):
    """
    Attributes:
        number_records_failed (Optional[str]): Number of records that failed in the bulk job Example: 0.
        number_records_processed (Optional[str]): Number of records that were processed in the bulk job Example: 0.
        retries (Optional[str]): Number of retries for the bulk job Example: 0.
        state (Optional[str]): The State Example: Closed.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    number_records_failed: Optional[str] = Field(
        alias="numberRecordsFailed", default=None
    )
    number_records_processed: Optional[str] = Field(
        alias="numberRecordsProcessed", default=None
    )
    retries: Optional[str] = Field(alias="retries", default=None)
    state: Optional[str] = Field(alias="state", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetBulkUploadJobInfoResponse"], src_dict: Dict[str, Any]):
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
