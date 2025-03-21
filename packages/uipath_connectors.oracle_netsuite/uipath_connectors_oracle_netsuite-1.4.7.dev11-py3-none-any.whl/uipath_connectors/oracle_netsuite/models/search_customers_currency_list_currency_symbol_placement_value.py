from enum import Enum


class SearchCustomersCurrencyListCurrencySymbolPlacementValue(str, Enum):
    AFTER_NUMBER = "_afterNumber"
    BEFORE_NUMBER = "_beforeNumber"

    def __str__(self) -> str:
        return str(self.value)
