from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SearchItemsSupplyReplenishmentMethodType(BaseModel):
    """
    Attributes:
        value (Optional[str]): Select one of the following Replenishment Methods to calculate item replenishment
                requirements:    * Reorder Point – To use Advanced Inventory Management settings for demand calculations instead
                of using Demand Planning.      This is the default setting for new item records.      Orders are created based
                on replenishment reminders generated from the Order Items page, Replenish Items, and Mass Create Work Orders.
                * Time Phased – To create orders based on item demand plans instead of the Advanced Inventory Management
                settings.      When you choose this setting, other fields on the record that are used by Advanced Inventory
                Management to calculate demand are no longer available. These unavailable fields are: Seasonal Demand, Build
                Point, Reorder Point, Preferred Stock Level, Safety Stock Days.      The Auto calculate settings are cleared and
                cannot be changed for Demand Per Day, Reorder Point, Preferred Stock Level, Lead Time.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsSupplyReplenishmentMethodType"], src_dict: Dict[str, Any]
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
