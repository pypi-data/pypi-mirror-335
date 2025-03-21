from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SearchItemsSupplyLotSizingMethodType(BaseModel):
    """
    Attributes:
        value (Optional[str]): Select a Lot Sizing Method:    * Lot For Lot – Orders are suggested for procurement based
                on the exact projections for that day. The suggested order quantity may vary from day to day depending on demand
                calculations.    * Fixed Lot Size – Orders are suggested for procurement based on a fixed amount or a multiple
                of the fixed amount.    * Periods of Supply – Generates aggregated purchase orders or work orders based on the
                overall demand requirements extended over a designated period, such as weekly or monthly.      For example,
                rather than creating multiple purchase orders for each instance of demand, you can consolidate into one order
                created from the demand planning engine for all items required within the next 2 weeks. By sending a
                consolidated purchase order to a vendor, the vendor can ship all items at one time rather than in multiple
                shipments, potentially resulting in reduced shipping costs.      Note: Be aware of costs from vendor holding
                charges. You can consolidate orders for a period, but after being consolidated, the Bill of Materials (BOM) for
                that specific work order on that specific level will also be used for subsequent levels.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsSupplyLotSizingMethodType"], src_dict: Dict[str, Any]
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
