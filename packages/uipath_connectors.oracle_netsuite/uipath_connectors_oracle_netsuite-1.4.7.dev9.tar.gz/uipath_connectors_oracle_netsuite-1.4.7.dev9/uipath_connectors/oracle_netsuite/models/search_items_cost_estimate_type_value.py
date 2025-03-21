from enum import Enum


class SearchItemsCostEstimateTypeValue(str, Enum):
    AVERAGE_COST = "_averageCost"
    CUSTOM = "_custom"
    DERIVED_FROM_MEMBER_ITEMS = "_derivedFromMemberItems"
    ITEM_DEFINED_COST = "_itemDefinedCost"
    LAST_PURCHASE_PRICE = "_lastPurchasePrice"
    PREFERRED_VENDOR_RATE = "_preferredVendorRate"
    PURCHASE_ORDER_RATE = "_purchaseOrderRate"
    PURCHASE_PRICE = "_purchasePrice"

    def __str__(self) -> str:
        return str(self.value)
