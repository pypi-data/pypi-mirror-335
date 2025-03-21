from enum import Enum


class SearchItemsVsoePermitDiscountValue(str, Enum):
    AS_ALLOWED = "_asAllowed"
    NEVER = "_never"

    def __str__(self) -> str:
        return str(self.value)
