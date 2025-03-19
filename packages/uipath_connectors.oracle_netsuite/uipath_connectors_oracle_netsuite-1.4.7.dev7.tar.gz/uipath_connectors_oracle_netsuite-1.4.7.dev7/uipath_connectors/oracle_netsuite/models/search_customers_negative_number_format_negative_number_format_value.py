from enum import Enum


class SearchCustomersNegativeNumberFormatNegativeNumberFormatValue(str, Enum):
    VALUE_0 = "_bracketSurrounded"
    VALUE_1 = "_minusSigned"

    def __str__(self) -> str:
        return str(self.value)
