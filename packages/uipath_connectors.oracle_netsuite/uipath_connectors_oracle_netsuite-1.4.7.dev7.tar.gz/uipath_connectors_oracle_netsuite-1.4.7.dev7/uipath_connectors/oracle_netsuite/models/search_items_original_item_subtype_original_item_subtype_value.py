from enum import Enum


class SearchItemsOriginalItemSubtypeOriginalItemSubtypeValue(str, Enum):
    VALUE_0 = "_forPurchase"
    VALUE_1 = "_forResale"
    VALUE_2 = "_forSale"

    def __str__(self) -> str:
        return str(self.value)
