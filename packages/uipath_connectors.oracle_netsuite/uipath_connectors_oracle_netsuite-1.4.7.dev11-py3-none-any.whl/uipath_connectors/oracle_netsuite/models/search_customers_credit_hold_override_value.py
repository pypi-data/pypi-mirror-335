from enum import Enum


class SearchCustomersCreditHoldOverrideValue(str, Enum):
    AUTO = "_auto"
    OFF = "_off"
    ON = "_on"

    def __str__(self) -> str:
        return str(self.value)
