from enum import Enum


class SearchCustomersSymbolPlacementSymbolPlacementValue(str, Enum):
    VALUE_0 = "_afterNumber"
    VALUE_1 = "_beforeNumber"

    def __str__(self) -> str:
        return str(self.value)
