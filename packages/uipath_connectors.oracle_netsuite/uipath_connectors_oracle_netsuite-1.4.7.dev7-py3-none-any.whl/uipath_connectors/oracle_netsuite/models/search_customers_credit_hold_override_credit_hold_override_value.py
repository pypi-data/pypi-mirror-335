from enum import Enum


class SearchCustomersCreditHoldOverrideCreditHoldOverrideValue(str, Enum):
    VALUE_0 = "_auto"
    VALUE_1 = "_on"
    VALUE_2 = "_off"

    def __str__(self) -> str:
        return str(self.value)
