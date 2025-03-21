from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.parameterized_search_request_in import ParameterizedSearchRequestIn


class ParameterizedSearchRequest(BaseModel):
    """
    Attributes:
        q (str): Pass a string to search
        default_limit (Optional[str]): The maximum number of results to return for each sobject (GET) or sobjects (POST)
                specified. The maximum defaultLimit is 2000
        division (Optional[str]): Filters search results based on the division field
        fields (Optional[str]): Pass one or more fields seperated by comma to retrieve in the response e.g. -
                FirstName,LastName,Id
        generate_schema (Optional[str]): The schema generate button
        in_ (Optional[ParameterizedSearchRequestIn]): Scope of fields to search. If you specify one or more scope
                values, the fields are returned for all found objects
        metadata (Optional[str]): Specifies if metadata should be returned in the response. No metadata is returned by
                default
        net_work_ids (Optional[list[str]]):
        offset (Optional[str]): The starting row offset into the result set returned. The maximum offset is 2000.
        overall_limit (Optional[str]): The maximum number of results to return across all sobject parameters specified.
                The maximum overallLimit is 2000.
        pricebook_id (Optional[str]): Filters product search results by a price book ID for only the Product2 object.
                The price book ID must be associated with the product that you’re searching for
        snippet (Optional[str]): The target length (maximum number of snippet characters) to return in Salesforce
                Knowledge article, case, case comment, feed, feed comment, idea, and idea comment search results.
        sobjects (Optional[str]): Select a Salesforce object to restrict the search
        spell_correction (Optional[bool]): Specifies whether spell correction is enabled for a user’s search. When set
                to true, spell correction is enabled for searches that support spell correction. The default value is true
        update_tracking (Optional[str]): Specifies a value of true to track keywords that are used in Salesforce
                Knowledge article searches only.
        update_view_stat (Optional[str]): Specifies a value of true to update an article’s view statistics. Valid only
                for Salesforce Knowledge article searches.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    q: str = Field(alias="q")
    default_limit: Optional[str] = Field(alias="defaultLimit", default=None)
    division: Optional[str] = Field(alias="division", default=None)
    fields: Optional[str] = Field(alias="fields", default=None)
    generate_schema: Optional[str] = Field(alias="generateSchema", default=None)
    in_: Optional["ParameterizedSearchRequestIn"] = Field(alias="in", default=None)
    metadata: Optional[str] = Field(alias="metadata", default=None)
    net_work_ids: Optional[list[str]] = Field(alias="netWorkIds", default=None)
    offset: Optional[str] = Field(alias="offset", default=None)
    overall_limit: Optional[str] = Field(alias="overallLimit", default=None)
    pricebook_id: Optional[str] = Field(alias="pricebookId", default=None)
    snippet: Optional[str] = Field(alias="snippet", default=None)
    sobjects: Optional[str] = Field(alias="sobjects", default=None)
    spell_correction: Optional[bool] = Field(alias="spellCorrection", default=None)
    update_tracking: Optional[str] = Field(alias="updateTracking", default=None)
    update_view_stat: Optional[str] = Field(alias="updateViewStat", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["ParameterizedSearchRequest"], src_dict: Dict[str, Any]):
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
