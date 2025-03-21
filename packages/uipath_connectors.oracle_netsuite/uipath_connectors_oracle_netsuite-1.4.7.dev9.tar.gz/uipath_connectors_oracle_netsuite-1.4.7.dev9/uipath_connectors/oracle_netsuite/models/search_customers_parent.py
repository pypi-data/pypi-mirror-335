from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_parent_type import SearchCustomersParentType


class SearchCustomersParent(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): If this customer is subcustomer of another customer or a smaller entity of another
                customer, select the larger parent customer.If you select a parent customer in this field, this record shows
                indented under the parent customer in the Customers list.
        internal_id (Optional[str]): If this customer is subcustomer of another customer or a smaller entity of another
                customer, select the larger parent customer.If you select a parent customer in this field, this record shows
                indented under the parent customer in the Customers list.
        name (Optional[str]): If this customer is subcustomer of another customer or a smaller entity of another
                customer, select the larger parent customer.If you select a parent customer in this field, this record shows
                indented under the parent customer in the Customers list.
        type_ (Optional[SearchCustomersParentType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchCustomersParentType"] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchCustomersParent"], src_dict: Dict[str, Any]):
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
