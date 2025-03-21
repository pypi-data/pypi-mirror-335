from enum import Enum


class SearchItemsOverallQuantityPricingTypeValue(str, Enum):
    BY_LINE_QUANTITY = "_byLineQuantity"
    BY_OVERALL_ITEM_QUANTITY = "_byOverallItemQuantity"
    BY_OVERALL_PARENT_QUANTITY = "_byOverallParentQuantity"
    BY_OVERALL_SCHEDULE_QUANTITY = "_byOverallScheduleQuantity"

    def __str__(self) -> str:
        return str(self.value)
