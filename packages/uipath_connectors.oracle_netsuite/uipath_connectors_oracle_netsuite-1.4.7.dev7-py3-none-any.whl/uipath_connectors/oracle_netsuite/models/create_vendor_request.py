from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.create_vendor_request_vendor_type import CreateVendorRequestVendorType
from ..models.create_vendor_request_subsidiary import CreateVendorRequestSubsidiary
from ..models.create_vendor_request_address_2 import CreateVendorRequestAddress2
from ..models.create_vendor_request_address_1 import CreateVendorRequestAddress1
from ..models.create_vendor_request_currency import CreateVendorRequestCurrency


class CreateVendorRequest(BaseModel):
    """
    Attributes:
        vendor_type (CreateVendorRequestVendorType):
        address1 (Optional[CreateVendorRequestAddress1]):
        address2 (Optional[CreateVendorRequestAddress2]):
        company_name (Optional[str]): The Company name Example: tstCustomerLeustean updated.
        currency (Optional[CreateVendorRequestCurrency]):
        email (Optional[str]): The Email Example: bogdan.leustean@yahoo.com.
        first_name (Optional[str]): The First name Example: ChurrosFirstN.
        last_name (Optional[str]): The Last name Example: ChurrosLastN2.
        middle_name (Optional[str]): The Middle name Example: ab.
        phone (Optional[str]): The Phone Example: +19999.
        salutation (Optional[str]): The Salutation Example: Mr.
        subsidiary (Optional[CreateVendorRequestSubsidiary]):
        url (Optional[str]): The Url Example: https://wwe.com.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    vendor_type: CreateVendorRequestVendorType = Field(alias="vendorType")
    address1: Optional["CreateVendorRequestAddress1"] = Field(
        alias="address1", default=None
    )
    address2: Optional["CreateVendorRequestAddress2"] = Field(
        alias="address2", default=None
    )
    company_name: Optional[str] = Field(alias="companyName", default=None)
    currency: Optional["CreateVendorRequestCurrency"] = Field(
        alias="currency", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    first_name: Optional[str] = Field(alias="firstName", default=None)
    last_name: Optional[str] = Field(alias="lastName", default=None)
    middle_name: Optional[str] = Field(alias="middleName", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    salutation: Optional[str] = Field(alias="salutation", default=None)
    subsidiary: Optional["CreateVendorRequestSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["CreateVendorRequest"], src_dict: Dict[str, Any]):
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
