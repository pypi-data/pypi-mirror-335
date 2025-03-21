from enum import Enum


class SearchCustomersNegativeNumberFormatValue(str, Enum):
    BRACKET_SURROUNDED = "_bracketSurrounded"
    MINUS_SIGNED = "_minusSigned"

    def __str__(self) -> str:
        return str(self.value)
