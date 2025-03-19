from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_tax_registration_list_customer_tax_registration_nexus_country import (
    SearchCustomersTaxRegistrationListCustomerTaxRegistrationNexusCountry,
)
from ..models.search_customers_record_ref import SearchCustomersRecordRef


class SearchCustomersTaxRegistrationListCustomerTaxRegistrationArrayItemRef(BaseModel):
    """
    Attributes:
        address (Optional[SearchCustomersRecordRef]):
        id (Optional[int]):
        nexus (Optional[SearchCustomersRecordRef]):
        nexus_country (Optional[SearchCustomersTaxRegistrationListCustomerTaxRegistrationNexusCountry]):
        tax_registration_number (Optional[str]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    address: Optional["SearchCustomersRecordRef"] = Field(alias="address", default=None)
    id: Optional[int] = Field(alias="id", default=None)
    nexus: Optional["SearchCustomersRecordRef"] = Field(alias="nexus", default=None)
    nexus_country: Optional[
        "SearchCustomersTaxRegistrationListCustomerTaxRegistrationNexusCountry"
    ] = Field(alias="nexusCountry", default=None)
    tax_registration_number: Optional[str] = Field(
        alias="taxRegistrationNumber", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type[
            "SearchCustomersTaxRegistrationListCustomerTaxRegistrationArrayItemRef"
        ],
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
