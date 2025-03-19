from enum import Enum


class SearchItemsOutOfStockBehaviorOutOfStockBehaviorValue(str, Enum):
    VALUE_0 = "_allowBackOrdersButDisplayOutOfStockMessage"
    VALUE_1 = "_allowBackOrdersWithNoOutOfStockMessage"
    VALUE_2 = "_default"
    VALUE_3 = "_disallowBackOrdersButDisplayOutOfStockMessage"
    VALUE_4 = "_removeItemWhenOutOfStock"

    def __str__(self) -> str:
        return str(self.value)
