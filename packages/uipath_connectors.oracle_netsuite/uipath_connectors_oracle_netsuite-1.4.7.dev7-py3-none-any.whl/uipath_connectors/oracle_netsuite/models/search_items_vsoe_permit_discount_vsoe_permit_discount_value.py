from enum import Enum


class SearchItemsVsoePermitDiscountVsoePermitDiscountValue(str, Enum):
    VALUE_0 = "_asAllowed"
    VALUE_1 = "_never"

    def __str__(self) -> str:
        return str(self.value)
