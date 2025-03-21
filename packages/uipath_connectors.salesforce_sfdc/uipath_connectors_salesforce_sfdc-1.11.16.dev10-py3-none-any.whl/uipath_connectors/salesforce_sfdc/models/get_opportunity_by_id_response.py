from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class GetOpportunityByIdResponse(BaseModel):
    """
    Attributes:
        account_id (Optional[str]): Type upto 3 characters of the name to select the account or pass account ID. ID can
                also be retrieved from the event trigger output Example: 0014x00000DXNnUAAX.
        amount (Optional[float]): Amount associated with the opportunity Example: 50000.5.
        campaign_id (Optional[str]): Type upto 3 characters of the name to select the campaign or pass campaign ID. ID
                can also be retrieved from the event trigger output Example: 7014x000000QLxmAAG.
        close_date (Optional[datetime.datetime]): Close date of the opportunity Example: 2022-09-12.
        contact_id (Optional[str]): Type upto 3 characters of the name to select the account or pass account ID. ID can
                also be retrieved from the event trigger output Example: 0034x000009oUnfAAE.
        description (Optional[str]): Additional details about the opportunity Example: this is test .
        id (Optional[str]): ID of the opportunity created in Salesforce Example: 0064x00000Fvzs0AAB.
        name (Optional[str]): Name of the opportunity Example: testnmae.
        owner_id (Optional[str]):  Example: 0054x000003qyoxAAA.
        probability (Optional[float]): Probability percentage of closure of the opportunity Example: 75.0.
        stage_name (Optional[str]): Current stage of the opportunity. Eg: Prospecting, Needs Analysis, Negotiation,
                Closed Won, closed Lost etc Example: Prospecting.
        type_ (Optional[str]):  Type of the opportunity. Eg. Existing customer, New customer etc. These values are
                customizable in Salesforce Example: Existing Customer - Upgrade.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    account_id: Optional[str] = Field(alias="AccountId", default=None)
    amount: Optional[float] = Field(alias="Amount", default=None)
    campaign_id: Optional[str] = Field(alias="CampaignId", default=None)
    close_date: Optional[datetime.datetime] = Field(alias="CloseDate", default=None)
    contact_id: Optional[str] = Field(alias="ContactId", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    id: Optional[str] = Field(alias="Id", default=None)
    name: Optional[str] = Field(alias="Name", default=None)
    owner_id: Optional[str] = Field(alias="OwnerId", default=None)
    probability: Optional[float] = Field(alias="Probability", default=None)
    stage_name: Optional[str] = Field(alias="StageName", default=None)
    type_: Optional[str] = Field(alias="Type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["GetOpportunityByIdResponse"], src_dict: Dict[str, Any]):
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
