from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

import datetime


class CreateOpportunityResponse(BaseModel):
    """
    Attributes:
        close_date (datetime.datetime): Close date of the opportunity Example: 2022-09-12.
        name (str): Name of the opportunity Example: testnmae.
        stage_name (str): Current stage of the opportunity. Eg: Prospecting, Needs Analysis, Negotiation, Closed Won,
                closed Lost etc Example: Prospecting.
        account_id (Optional[str]): Type upto 3 characters of the name to select the account or pass account ID. ID can
                also be retrieved from the event trigger output Example: 0014x00000DXNnUAAX.
        amount (Optional[float]): Amount associated with the opportunity Example: 50000.5.
        campaign_id (Optional[str]): Type upto 3 characters of the name to select the campaign or pass campaign ID. ID
                can also be retrieved from the event trigger output Example: 7014x000000QLxmAAG.
        contact_id (Optional[str]): Type upto 3 characters of the name to select the account or pass account ID. ID can
                also be retrieved from the event trigger output Example: 0034x000009oUnfAAE.
        description (Optional[str]): Additional details about the opportunity Example: this is test .
        id (Optional[str]): ID of the opportunity created in Salesforce Example: 0064x00000Fvzs0AAB.
        next_step (Optional[str]): Details of next step to be taken with the opportunity Example: This is next step.
        probability (Optional[float]): Probability percentage of closure of the opportunity Example: 75.0.
        type_ (Optional[str]):  Type of the opportunity. Eg. Existing customer, New customer etc. These values are
                customizable in Salesforce Example: Existing Customer - Upgrade.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    close_date: datetime.datetime = Field(alias="CloseDate")
    name: str = Field(alias="Name")
    stage_name: str = Field(alias="StageName")
    account_id: Optional[str] = Field(alias="AccountId", default=None)
    amount: Optional[float] = Field(alias="Amount", default=None)
    campaign_id: Optional[str] = Field(alias="CampaignId", default=None)
    contact_id: Optional[str] = Field(alias="ContactId", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    id: Optional[str] = Field(alias="Id", default=None)
    next_step: Optional[str] = Field(alias="NextStep", default=None)
    probability: Optional[float] = Field(alias="Probability", default=None)
    type_: Optional[str] = Field(alias="Type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateOpportunityResponse"], src_dict: Dict[str, Any]):
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
