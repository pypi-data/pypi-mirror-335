from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_vsoe_permit_discount_vsoe_permit_discount_value import (
    SearchItemsVsoePermitDiscountVsoePermitDiscountValue,
)


class SearchItemsVsoePermitDiscount(BaseModel):
    """
    Attributes:
        value (Optional[SearchItemsVsoePermitDiscountVsoePermitDiscountValue]): Set one of the following options to
                determine how discounts are handled for this item._asAllowed - Allows a portion of an applicable discount to be
                applied against this item if its status is Delivered when the VSOE allocation is performed._never - Does not
                allow a discount to be applied against this item when the VSOE allocation is performed. This selection would be
                common for a Specified Upgrade. Note: The default for this field is _asAllowed.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[SearchItemsVsoePermitDiscountVsoePermitDiscountValue] = Field(
        alias="value", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsVsoePermitDiscount"], src_dict: Dict[str, Any]):
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
