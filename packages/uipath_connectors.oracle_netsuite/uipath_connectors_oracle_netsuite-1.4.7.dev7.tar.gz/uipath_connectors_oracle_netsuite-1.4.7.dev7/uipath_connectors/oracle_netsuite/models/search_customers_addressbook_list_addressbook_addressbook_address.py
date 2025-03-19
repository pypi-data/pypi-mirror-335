from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_addressbook_list_addressbook_addressbook_address_country import (
    SearchCustomersAddressbookListAddressbookAddressbookAddressCountry,
)
from ..models.search_customers_addressbook_list_addressbook_addressbook_address_null_field_list import (
    SearchCustomersAddressbookListAddressbookAddressbookAddressNullFieldList,
)
from ..models.search_customers_addressbook_list_addressbook_addressbook_address_custom_field_list import (
    SearchCustomersAddressbookListAddressbookAddressbookAddressCustomFieldList,
)


class SearchCustomersAddressbookListAddressbookAddressbookAddress(BaseModel):
    """
    Attributes:
        addr1 (Optional[str]):
        addr2 (Optional[str]):
        addr3 (Optional[str]):
        addr_phone (Optional[str]):
        addr_text (Optional[str]):
        addressee (Optional[str]):
        attention (Optional[str]):
        city (Optional[str]):
        country (Optional[SearchCustomersAddressbookListAddressbookAddressbookAddressCountry]):
        custom_field_list (Optional[SearchCustomersAddressbookListAddressbookAddressbookAddressCustomFieldList]):
        internal_id (Optional[str]):
        null_field_list (Optional[SearchCustomersAddressbookListAddressbookAddressbookAddressNullFieldList]):
        override (Optional[bool]):
        state (Optional[str]):
        zip_ (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    addr1: Optional[str] = Field(alias="addr1", default=None)
    addr2: Optional[str] = Field(alias="addr2", default=None)
    addr3: Optional[str] = Field(alias="addr3", default=None)
    addr_phone: Optional[str] = Field(alias="addrPhone", default=None)
    addr_text: Optional[str] = Field(alias="addrText", default=None)
    addressee: Optional[str] = Field(alias="addressee", default=None)
    attention: Optional[str] = Field(alias="attention", default=None)
    city: Optional[str] = Field(alias="city", default=None)
    country: Optional[
        "SearchCustomersAddressbookListAddressbookAddressbookAddressCountry"
    ] = Field(alias="country", default=None)
    custom_field_list: Optional[
        "SearchCustomersAddressbookListAddressbookAddressbookAddressCustomFieldList"
    ] = Field(alias="customFieldList", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    null_field_list: Optional[
        "SearchCustomersAddressbookListAddressbookAddressbookAddressNullFieldList"
    ] = Field(alias="nullFieldList", default=None)
    override: Optional[bool] = Field(alias="override", default=None)
    state: Optional[str] = Field(alias="state", default=None)
    zip_: Optional[str] = Field(alias="zip", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchCustomersAddressbookListAddressbookAddressbookAddress"],
        src_dict: Dict[str, Any],
    ):
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
