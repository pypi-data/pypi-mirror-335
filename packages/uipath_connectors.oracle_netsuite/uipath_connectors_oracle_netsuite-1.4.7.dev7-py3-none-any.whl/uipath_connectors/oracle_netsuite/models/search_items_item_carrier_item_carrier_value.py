from enum import Enum


class SearchItemsItemCarrierItemCarrierValue(str, Enum):
    VALUE_0 = "_fedexUspsMore"
    VALUE_1 = "_ups"

    def __str__(self) -> str:
        return str(self.value)
