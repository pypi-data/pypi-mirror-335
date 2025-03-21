from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class CreateLeadResponse(BaseModel):
    """
    Attributes:
        company (str): Company name of the lead Example: testCompany.
        last_name (str): Last name of the lead Example: last name test create.
        city (Optional[str]): City of the lead Example: New york.
        country (Optional[str]): Country of the lead Example: USA.
        description (Optional[str]): Additional description of the lead Example: this is teest.
        email (Optional[str]): Email address of the lead Example: yad.moo@gmail.com.
        first_name (Optional[str]): First name of the lead Example: monu.
        id (Optional[str]): ID of the lead that gets created in Salesforce Example: 00Q4x00000KmY3KEAV.
        lead_source (Optional[str]): Source of the lead. Eg. Web, Phone Inquiry, Partner Referral, Purchased List etc.
                These values are customizable Example: Web.
        mobile_phone (Optional[str]): Mobile phone number of the lead Example: +91888890000.
        phone (Optional[str]): Phone number of the lead Example: +918888900000.
        postal_code (Optional[str]): Postal code of the lead Example: 100011.
        rating (Optional[str]): Rating of the lead. Eg. Hot, Warm, Cold. These values are customizable Example: Hot.
        status (Optional[str]): Status of the lead. For example, Open - Not contacted, Working - Contacted, Closed -
                Converted, Closed - Not Converted etc Example: Open - Not Contacted.
        street (Optional[str]): Street name of the lead Example: 12th delmont street.
        title (Optional[str]): Title of the lead Example: New Title.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    company: str = Field(alias="Company")
    last_name: str = Field(alias="LastName")
    city: Optional[str] = Field(alias="City", default=None)
    country: Optional[str] = Field(alias="Country", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    email: Optional[str] = Field(alias="Email", default=None)
    first_name: Optional[str] = Field(alias="FirstName", default=None)
    id: Optional[str] = Field(alias="Id", default=None)
    lead_source: Optional[str] = Field(alias="LeadSource", default=None)
    mobile_phone: Optional[str] = Field(alias="MobilePhone", default=None)
    phone: Optional[str] = Field(alias="Phone", default=None)
    postal_code: Optional[str] = Field(alias="PostalCode", default=None)
    rating: Optional[str] = Field(alias="Rating", default=None)
    status: Optional[str] = Field(alias="Status", default=None)
    street: Optional[str] = Field(alias="Street", default=None)
    title: Optional[str] = Field(alias="Title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateLeadResponse"], src_dict: Dict[str, Any]):
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
