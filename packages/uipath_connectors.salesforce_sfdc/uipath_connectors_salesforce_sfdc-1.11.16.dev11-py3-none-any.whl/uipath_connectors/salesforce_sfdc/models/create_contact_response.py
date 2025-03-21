from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class CreateContactResponse(BaseModel):
    """
    Attributes:
        last_name (str): Last name of the contact Example: last name test create.
        account_id (Optional[str]): Type upto 3 characters of the name to select the account or pass account ID. ID can
                also be retrieved from the event trigger output Example: 1234567qwer.
        description (Optional[str]): Additional details of the contact Example: this is teest.
        email (Optional[str]): Email address of the contact Example: yad.mono@gmail.com.
        first_name (Optional[str]): First name of the contact Example: mona.
        id (Optional[str]): ID of the contact generated in the Salesforce system Example: 1234567qwer.
        mailing_city (Optional[str]): City of the contact to be added Example: New york.
        mailing_country (Optional[str]): Country of the contact Example: USA.
        mailing_postal_code (Optional[str]): Postal code of the contact Example: 100011.
        mailing_street (Optional[str]): Street address of the contact Example: 12th delmont street.
        mobile_phone (Optional[str]): Mobile phone number of the contact Example: +918888890000.
        phone (Optional[str]): Business phone number of the contact Example: +9188888900000.
        title (Optional[str]): Designation of the contact Example: Prospect.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    last_name: str = Field(alias="LastName")
    account_id: Optional[str] = Field(alias="AccountId", default=None)
    description: Optional[str] = Field(alias="Description", default=None)
    email: Optional[str] = Field(alias="Email", default=None)
    first_name: Optional[str] = Field(alias="FirstName", default=None)
    id: Optional[str] = Field(alias="Id", default=None)
    mailing_city: Optional[str] = Field(alias="MailingCity", default=None)
    mailing_country: Optional[str] = Field(alias="MailingCountry", default=None)
    mailing_postal_code: Optional[str] = Field(alias="MailingPostalCode", default=None)
    mailing_street: Optional[str] = Field(alias="MailingStreet", default=None)
    mobile_phone: Optional[str] = Field(alias="MobilePhone", default=None)
    phone: Optional[str] = Field(alias="Phone", default=None)
    title: Optional[str] = Field(alias="Title", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateContactResponse"], src_dict: Dict[str, Any]):
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
