from enum import Enum


class SearchItemsCostEstimateTypeCostEstimateTypeValue(str, Enum):
    VALUE_0 = "_averageCost"
    VALUE_1 = "_custom"
    VALUE_2 = "_derivedFromMemberItems"
    VALUE_3 = "_itemDefinedCost"
    VALUE_4 = "_lastPurchasePrice"
    VALUE_5 = "_preferredVendorRate"
    VALUE_6 = "_purchaseOrderRate"
    VALUE_7 = "_purchasePrice"

    def __str__(self) -> str:
        return str(self.value)
