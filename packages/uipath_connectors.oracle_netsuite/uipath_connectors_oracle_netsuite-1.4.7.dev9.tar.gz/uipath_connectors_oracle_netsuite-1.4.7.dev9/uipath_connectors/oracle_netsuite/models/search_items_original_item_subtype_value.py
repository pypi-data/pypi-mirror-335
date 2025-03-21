from enum import Enum


class SearchItemsOriginalItemSubtypeValue(str, Enum):
    FOR_PURCHASE = "_forPurchase"
    FOR_RESALE = "_forResale"
    FOR_SALE = "_forSale"

    def __str__(self) -> str:
        return str(self.value)
