from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_soft_descriptor_type import SearchItemsSoftDescriptorType


class SearchItemsSoftDescriptor(BaseModel):
    """
    Attributes:
        external_id (Optional[str]): In the Soft Descriptor list, select the name that will appear on the customer's
                credit card statement when this item is purchased.Enter soft descriptors to select in this field at Setup >
                Accounting > Payment Processing > Credit Card Soft Descriptors.
        internal_id (Optional[str]): In the Soft Descriptor list, select the name that will appear on the customer's
                credit card statement when this item is purchased.Enter soft descriptors to select in this field at Setup >
                Accounting > Payment Processing > Credit Card Soft Descriptors.
        name (Optional[str]): In the Soft Descriptor list, select the name that will appear on the customer's credit
                card statement when this item is purchased.Enter soft descriptors to select in this field at Setup > Accounting
                > Payment Processing > Credit Card Soft Descriptors.
        type_ (Optional[SearchItemsSoftDescriptorType]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    external_id: Optional[str] = Field(alias="externalId", default=None)
    internal_id: Optional[str] = Field(alias="internalId", default=None)
    name: Optional[str] = Field(alias="name", default=None)
    type_: Optional["SearchItemsSoftDescriptorType"] = Field(alias="type", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsSoftDescriptor"], src_dict: Dict[str, Any]):
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
