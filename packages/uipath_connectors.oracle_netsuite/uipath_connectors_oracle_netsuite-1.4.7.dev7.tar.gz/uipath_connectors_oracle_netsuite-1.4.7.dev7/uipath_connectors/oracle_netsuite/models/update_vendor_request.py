from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_vendor_request_vendor_type import UpdateVendorRequestVendorType
from ..models.update_vendor_request_parent import UpdateVendorRequestParent
from ..models.update_vendor_request_entity_status import UpdateVendorRequestEntityStatus
from ..models.update_vendor_request_address_2 import UpdateVendorRequestAddress2
from ..models.update_vendor_request_currency import UpdateVendorRequestCurrency
from ..models.update_vendor_request_subsidiary import UpdateVendorRequestSubsidiary


class UpdateVendorRequest(BaseModel):
    """
    Attributes:
        vendor_type (UpdateVendorRequestVendorType):
        address2 (Optional[UpdateVendorRequestAddress2]):
        company_name (Optional[str]): The Company name Example: tstCustomerLeustean updated.
        currency (Optional[UpdateVendorRequestCurrency]):
        email (Optional[str]): The Email Example: bogdan.leustean@yahoo.com.
        entity_status (Optional[UpdateVendorRequestEntityStatus]):
        first_name (Optional[str]): The First name Example: ChurrosFirstN.
        is_inactive (Optional[bool]): The Is inactive
        last_name (Optional[str]): The Last name Example: ChurrosLastN2.
        middle_name (Optional[str]): The Middle name Example: ab.
        parent (Optional[UpdateVendorRequestParent]):
        phone (Optional[str]): The Phone Example: +19999.
        salutation (Optional[str]): The Salutation Example: Mr.
        subsidiary (Optional[UpdateVendorRequestSubsidiary]):
        url (Optional[str]): The Url Example: https://wwe.com.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    vendor_type: UpdateVendorRequestVendorType = Field(alias="vendorType")
    address2: Optional["UpdateVendorRequestAddress2"] = Field(
        alias="address2", default=None
    )
    company_name: Optional[str] = Field(alias="companyName", default=None)
    currency: Optional["UpdateVendorRequestCurrency"] = Field(
        alias="currency", default=None
    )
    email: Optional[str] = Field(alias="email", default=None)
    entity_status: Optional["UpdateVendorRequestEntityStatus"] = Field(
        alias="entityStatus", default=None
    )
    first_name: Optional[str] = Field(alias="firstName", default=None)
    is_inactive: Optional[bool] = Field(alias="isInactive", default=None)
    last_name: Optional[str] = Field(alias="lastName", default=None)
    middle_name: Optional[str] = Field(alias="middleName", default=None)
    parent: Optional["UpdateVendorRequestParent"] = Field(alias="parent", default=None)
    phone: Optional[str] = Field(alias="phone", default=None)
    salutation: Optional[str] = Field(alias="salutation", default=None)
    subsidiary: Optional["UpdateVendorRequestSubsidiary"] = Field(
        alias="subsidiary", default=None
    )
    url: Optional[str] = Field(alias="url", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["UpdateVendorRequest"], src_dict: Dict[str, Any]):
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
