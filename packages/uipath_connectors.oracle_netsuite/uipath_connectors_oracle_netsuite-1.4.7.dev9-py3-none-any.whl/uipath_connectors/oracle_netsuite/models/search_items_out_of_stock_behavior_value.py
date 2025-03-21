from enum import Enum


class SearchItemsOutOfStockBehaviorValue(str, Enum):
    ALLOW_BACK_ORDERS_BUT_DISPLAY_OUT_OF_STOCK_MESSAGE = (
        "_allowBackOrdersButDisplayOutOfStockMessage"
    )
    ALLOW_BACK_ORDERS_WITH_NO_OUT_OF_STOCK_MESSAGE = (
        "_allowBackOrdersWithNoOutOfStockMessage"
    )
    DEFAULT = "_default"
    DISALLOW_BACK_ORDERS_BUT_DISPLAY_OUT_OF_STOCK_MESSAGE = (
        "_disallowBackOrdersButDisplayOutOfStockMessage"
    )
    REMOVE_ITEM_WHEN_OUT_OF_STOCK = "_removeItemWhenOutOfStock"

    def __str__(self) -> str:
        return str(self.value)
