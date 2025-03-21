from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type



class SearchItemsCreateRevenuePlansOnType(BaseModel):
    """
    Attributes:
        value (Optional[str]): Select the event that triggers creation of revenue recognition plans. Match the event
                with the amount source of the item's revenue recognition rule.    * Revenue Arrangement Creation - Revenue plans
                can be created when the revenue arrangement is created. Use this option with rules that have Event-Amount as the
                Amount Source.    * Billing - Revenue plans can be created when the sales order is billed and from stand-alone
                cash sales, invoices, credit memos, and cash refunds. Use this option with rules that have Event-Percent based
                on amount as the Amount Source.    * Fulfillment - This option is available only when Advanced Shipping is
                enabled. Revenue plans can be created upon fulfillment. Use this option with rules that have Event-Percent based
                on quantity as the Amount Source.    * Project Progress - This option is available only when the Projects
                feature is enabled. Use this option with rules that have Event-Percent Complete as the Amount Source.
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    value: Optional[str] = Field(alias="value", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchItemsCreateRevenuePlansOnType"], src_dict: Dict[str, Any]
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
