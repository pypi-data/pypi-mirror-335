from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_items_cost_estimate_type_cost_estimate_type_value import (
    SearchItemsCostEstimateTypeCostEstimateTypeValue,
)


class SearchItemsCostEstimateType(BaseModel):
    """
    Attributes:
        value (Optional[SearchItemsCostEstimateTypeCostEstimateTypeValue]): The Cost Estimate Type determines what value
                NetSuite uses to calculate estimated Gross Profit.The estimated Gross Profit for Items on a transaction provides
                the data needed to calculate the total estimated Gross Profit on that transaction.The individual line items that
                you enter in a transaction determine the amounts that post when you process that transaction.The following Cost
                Estimate Types on Items are available:    * Item Defined Cost - a user-defined amount, entered into the Item
                Defined Cost field on the Item definition page.    * Average Cost - NetSuite calculates an average cost of the
                units purchased.     * Last Purchase Price - This field displays the most recent purchase price of the item as
                determined by purchase order receipt transactions.     * Purchase Price - Price entered that you pay for this
                item. If you do not enter a price, then the most recent purchase price from purchase orders provides the price
                for this item by default.    * Preferred Vendor Rate - This option is only used if the Multi-Vendor feature is
                enabled and multiple vendors supply the same item.          o First priority is to use the preferred vendor rate
                if defined on the Item record.          o Next priority would be to use the purchase price.          o Last
                priority would be the purchase order rate. (Initially this uses the preferred vendor rate cost, and then after a
                purchase order is entered, this type uses the most recent actual purchase order rate. Special orders and drop-
                shipped items use this cost information.)    * Derived from member items - Total costs of items currently
                included in a kit. This Cost Estimate Type only applies to kits and sums the estimated costs of each item in the
                kit, based on each of their individual Cost Estimate Types. Uses the latest definition of the kit, not its
                historical definition.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[SearchItemsCostEstimateTypeCostEstimateTypeValue] = Field(
        alias="value", default=None
    )

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsCostEstimateType"], src_dict: Dict[str, Any]):
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
