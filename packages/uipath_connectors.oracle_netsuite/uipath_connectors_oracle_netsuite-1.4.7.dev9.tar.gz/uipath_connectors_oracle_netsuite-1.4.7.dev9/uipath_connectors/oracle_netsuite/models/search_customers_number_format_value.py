from enum import Enum


class SearchCustomersNumberFormatValue(str, Enum):
    APOSTROPHE_AS_DIGIT_GROUP_SEPARATOR_AND_DECIMAL_COMMA = (
        "_apostropheAsDigitGroupSeparatorAndDecimalComma"
    )
    APOSTROPHE_AS_DIGIT_GROUP_SEPARATOR_AND_DECIMAL_POINT = (
        "_apostropheAsDigitGroupSeparatorAndDecimalPoint"
    )
    COMMA_AS_DIGIT_GROUP_SEPARATOR_AND_DECIMAL_POINT = (
        "_commaAsDigitGroupSeparatorAndDecimalPoint"
    )
    POINT_AS_DIGIT_GROUP_SEPARATOR_AND_DECIMAL_COMMA = (
        "_pointAsDigitGroupSeparatorAndDecimalComma"
    )
    SPACE_AS_DIGIT_GROUP_SEPARATOR_AND_DECIMAL_COMMA = (
        "_spaceAsDigitGroupSeparatorAndDecimalComma"
    )
    SPACE_AS_DIGIT_GROUP_SEPARATOR_AND_DECIMAL_POINT = (
        "_spaceAsDigitGroupSeparatorAndDecimalPoint"
    )

    def __str__(self) -> str:
        return str(self.value)
