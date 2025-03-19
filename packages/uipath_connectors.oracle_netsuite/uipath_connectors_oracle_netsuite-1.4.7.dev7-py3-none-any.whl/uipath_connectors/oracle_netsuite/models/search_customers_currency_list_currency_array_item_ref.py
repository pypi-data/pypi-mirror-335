from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Dict, Optional, Type

from ..models.search_customers_currency_list_currency_symbol_placement import (
    SearchCustomersCurrencyListCurrencySymbolPlacement,
)
from ..models.search_customers_record_ref import SearchCustomersRecordRef


class SearchCustomersCurrencyListCurrencyArrayItemRef(BaseModel):
    """
    Attributes:
        balance (Optional[float]):
        consol_balance (Optional[float]):
        consol_deposit_balance (Optional[float]):
        consol_overdue_balance (Optional[float]):
        consol_unbilled_orders (Optional[float]):
        currency (Optional[SearchCustomersRecordRef]):
        deposit_balance (Optional[float]):
        display_symbol (Optional[str]):
        overdue_balance (Optional[float]):
        override_currency_format (Optional[bool]):
        symbol_placement (Optional[SearchCustomersCurrencyListCurrencySymbolPlacement]):
        unbilled_orders (Optional[float]):
    """

    model_config = ConfigDict(extra="allow", populate_by_name=True)

    balance: Optional[float] = Field(alias="balance", default=None)
    consol_balance: Optional[float] = Field(alias="consolBalance", default=None)
    consol_deposit_balance: Optional[float] = Field(
        alias="consolDepositBalance", default=None
    )
    consol_overdue_balance: Optional[float] = Field(
        alias="consolOverdueBalance", default=None
    )
    consol_unbilled_orders: Optional[float] = Field(
        alias="consolUnbilledOrders", default=None
    )
    currency: Optional["SearchCustomersRecordRef"] = Field(
        alias="currency", default=None
    )
    deposit_balance: Optional[float] = Field(alias="depositBalance", default=None)
    display_symbol: Optional[str] = Field(alias="displaySymbol", default=None)
    overdue_balance: Optional[float] = Field(alias="overdueBalance", default=None)
    override_currency_format: Optional[bool] = Field(
        alias="overrideCurrencyFormat", default=None
    )
    symbol_placement: Optional["SearchCustomersCurrencyListCurrencySymbolPlacement"] = (
        Field(alias="symbolPlacement", default=None)
    )
    unbilled_orders: Optional[float] = Field(alias="unbilledOrders", default=None)

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump(exclude_none=True, by_alias=True)

    @classmethod
    def from_dict(
        cls: Type["SearchCustomersCurrencyListCurrencyArrayItemRef"],
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
