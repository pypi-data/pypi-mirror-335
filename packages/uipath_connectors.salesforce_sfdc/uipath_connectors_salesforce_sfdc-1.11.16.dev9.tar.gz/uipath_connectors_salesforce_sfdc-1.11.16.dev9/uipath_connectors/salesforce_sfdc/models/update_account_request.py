from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class UpdateAccountRequest(BaseModel):
    """
    Attributes:
        account_number (Optional[str]): The user-defined external identifier of the account Example: CC978213.
        account_source (Optional[str]): Source from which the account/company was received. For example, Web, Phone,
                Twitter etc. Values are customizable Example: Web.
        billing_city (Optional[str]): City to which the account would be billed Example: New york.
        billing_country (Optional[str]): Country in which the account would be billed Example: USA.
        billing_postal_code (Optional[str]): Postal code to which the account would be billed Example: 100011.
        billing_street (Optional[str]): Street address to which the account would be billed Example: 12th delmont
                street.
        description (Optional[str]): Additional details about the account Example: this is teest.
        industry (Optional[str]): Industry to which the account belongs. For example, Technology, Finance, Retail, Other
                etc. These values are customizable Example: Agriculture.
        name (Optional[str]): Name of the account Example: test account create.
        owner_id (Optional[str]): Type upto 3 characters of the name to select the account owner or pass owner ID
                Example: testId.
        ownership (Optional[str]): Specifies the type of Ownership. Eg. Public, Private, Subsidiary etc. The values for
                this are customizable Example: Public.
        phone (Optional[str]): Phone number of the account Example: +9188888900000.
        type_ (Optional[str]): Type of the account. Eg. Prospect, Customer, Partner. The values for this are
                customizable Example: Prospect.
        website (Optional[str]): Website belonging to the account Example: gmail.com.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    account_number: Optional[str] = Field(alias="AccountNumber", default=None)
    account_source: Optional[str] = Field(alias="AccountSource", default=None)
    billing_city: Optional[str] = Field(alias="BillingCity", default=None)
    billing_country: Optional[str] = Field(alias="BillingCountry", default=None)
    billing_postal_code: Optional[str] = Field(alias="BillingPostalCode", default=None)
    billing_street: Optional[str] = Field(alias="BillingStreet", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    industry: Optional[str] = Field(alias="Industry", default=None)
    name: Optional[str] = Field(alias="Name", default=None)
    owner_id: Optional[str] = Field(alias="OwnerId", default=None)
    ownership: Optional[str] = Field(alias="Ownership", default=None)
    phone: Optional[str] = Field(alias="Phone", default=None)
    type_: Optional[str] = Field(alias="Type", default=None)
    website: Optional[str] = Field(alias="Website", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateAccountRequest"], src_dict: Dict[str, Any]):
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
