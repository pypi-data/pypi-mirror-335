from enum import Enum


class SearchCustomersNumberFormatNumberFormatValue(str, Enum):
    VALUE_0 = "_spaceAsDigitGroupSeparatorAndDecimalComma"
    VALUE_1 = "_spaceAsDigitGroupSeparatorAndDecimalPoint"
    VALUE_2 = "_commaAsDigitGroupSeparatorAndDecimalPoint"
    VALUE_3 = "_pointAsDigitGroupSeparatorAndDecimalComma"
    VALUE_4 = "_apostropheAsDigitGroupSeparatorAndDecimalComma"
    VALUE_5 = "_apostropheAsDigitGroupSeparatorAndDecimalPoint"

    def __str__(self) -> str:
        return str(self.value)
