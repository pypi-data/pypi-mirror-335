from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_customer_response_addressbook_list_addressbook_addressbook_address_country import (
    UpdateCustomerResponseAddressbookListAddressbookAddressbookAddressCountry,
)


class UpdateCustomerResponseAddressbookListAddressbookAddressbookAddress(BaseModel):
    """
    Attributes:
        addr1 (Optional[str]): The Addressbook list addressbook address addr 1 Example: kukatpally.
        addr2 (Optional[str]): The Addressbook list addressbook address addr 2 Example: knr.
        addr_text (Optional[str]): The Addressbook list addressbook address addr text Example: tstCustomerLeustean
                fdsfsd
                kukatpally
                knr
                Hyd telanagana 485885485
                India.
        addressee (Optional[str]): The Addressbook list addressbook address addressee Example: tstCustomerLeustean
                fdsfsd.
        city (Optional[str]): The Addressbook list addressbook address city Example: Hyd.
        country (Optional[UpdateCustomerResponseAddressbookListAddressbookAddressbookAddressCountry]):
        override (Optional[bool]): The Addressbook list addressbook address override
        state (Optional[str]): The Addressbook list addressbook address state Example: telanagana.
        zip_ (Optional[str]): The Addressbook list addressbook address zip Example: 485885485.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    addr1: Optional[str] = Field(alias="addr1", default=None)
    addr2: Optional[str] = Field(alias="addr2", default=None)
    addr_text: Optional[str] = Field(alias="addrText", default=None)
    addressee: Optional[str] = Field(alias="addressee", default=None)
    city: Optional[str] = Field(alias="city", default=None)
    country: Optional[
        "UpdateCustomerResponseAddressbookListAddressbookAddressbookAddressCountry"
    ] = Field(alias="country", default=None)
    override: Optional[bool] = Field(alias="override", default=None)
    state: Optional[str] = Field(alias="state", default=None)
    zip_: Optional[str] = Field(alias="zip", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["UpdateCustomerResponseAddressbookListAddressbookAddressbookAddress"],
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
