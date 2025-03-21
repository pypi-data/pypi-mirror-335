from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.update_customer_response_addressbook_list_addressbook_addressbook_address import (
    UpdateCustomerResponseAddressbookListAddressbookAddressbookAddress,
)


class UpdateCustomerResponseAddressbookListAddressbookArrayItemRef(BaseModel):
    """
    Attributes:
        addressbook_address (Optional[UpdateCustomerResponseAddressbookListAddressbookAddressbookAddress]):
        default_billing (Optional[bool]): The Addressbook list addressbook default billing
        default_shipping (Optional[bool]): The Addressbook list addressbook default shipping Example: True.
        internal_id (Optional[str]): The Addressbook list addressbook internal ID Example: 164614.
        is_residential (Optional[bool]): The Addressbook list addressbook is residential
        label (Optional[str]): The Addressbook list addressbook label Example: kukatpally.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    addressbook_address: Optional[
        "UpdateCustomerResponseAddressbookListAddressbookAddressbookAddress"
    ] = Field(alias="addressbookAddress", default=None)
    default_billing: Optional[bool] = Field(alias="defaultBilling", default=None)
    default_shipping: Optional[bool] = Field(alias="defaultShipping", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    is_residential: Optional[bool] = Field(alias="isResidential", default=None)
    label: Optional[str] = Field(alias="label", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["UpdateCustomerResponseAddressbookListAddressbookArrayItemRef"],
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
