from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SearchItemsDemandSourceType(BaseModel):
    """
    Attributes:
        value (Optional[str]): Select a Demand Source to determine where demand data is sourced for an item.    *
                Forecast from Demand Plan – Source only the item's demand plan record.      Note: A sales order with a related
                work order generates a supply plan for the sales order. The Mass Create Work Orders page automatically suggests
                a supply for the sales order.    * Entered and Planned Orders – Source open orders and use the expected ship
                date as the demand date. If the item is a member of an assembly, demand for the assembly is included demand
                calculations for the item.    * Order and Forecast – Calculates demand for an item by including both the
                forecast amount and the amount on orders that have been entered.      Forecast demand for an item is calculated
                by combining (Quantity forecast over time) + (quantity on sales orders and invoices entered)    * Forecast
                Consumption – Calculates demand for an item by subtracting from the forecast quantity any item quantities on
                orders entered. This removes duplication if an order is already included as part of a forecast.      Demand for
                an item is calculated as (Quantity forecast over time) - (quantity on sales orders and invoices entered).
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(cls: Type["SearchItemsDemandSourceType"], src_dict: Dict[str, Any]):
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
