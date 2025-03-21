from enum import Enum


class SearchCustomersSymbolPlacementValue(str, Enum):
    AFTER_NUMBER = "_afterNumber"
    BEFORE_NUMBER = "_beforeNumber"

    def __str__(self) -> str:
        return str(self.value)
