from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_item_pricing_list_item_pricing_currency import (
    SearchCustomersItemPricingListItemPricingCurrency,
)
from ..models.search_customers_item_pricing_list_item_pricing_item import (
    SearchCustomersItemPricingListItemPricingItem,
)
from ..models.search_customers_item_pricing_list_item_pricing_level import (
    SearchCustomersItemPricingListItemPricingLevel,
)


class SearchCustomersItemPricingListItemPricingArrayItemRef(BaseModel):
    """
    Attributes:
        currency (Optional[SearchCustomersItemPricingListItemPricingCurrency]):
        item (Optional[SearchCustomersItemPricingListItemPricingItem]):
        level (Optional[SearchCustomersItemPricingListItemPricingLevel]):
        price (Optional[float]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    currency: Optional["SearchCustomersItemPricingListItemPricingCurrency"] = Field(
        alias="currency", default=None
    )
    item: Optional["SearchCustomersItemPricingListItemPricingItem"] = Field(
        alias="item", default=None
    )
    level: Optional["SearchCustomersItemPricingListItemPricingLevel"] = Field(
        alias="level", default=None
    )
    price: Optional[float] = Field(alias="price", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchCustomersItemPricingListItemPricingArrayItemRef"],
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
