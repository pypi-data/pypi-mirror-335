from enum import Enum


class SearchItemsOverallQuantityPricingTypeOverallQuantityPricingTypeValue(str, Enum):
    VALUE_0 = "_byLineQuantity"
    VALUE_1 = "_byOverallItemQuantity"
    VALUE_2 = "_byOverallParentQuantity"
    VALUE_3 = "_byOverallScheduleQuantity"

    def __str__(self) -> str:
        return str(self.value)
