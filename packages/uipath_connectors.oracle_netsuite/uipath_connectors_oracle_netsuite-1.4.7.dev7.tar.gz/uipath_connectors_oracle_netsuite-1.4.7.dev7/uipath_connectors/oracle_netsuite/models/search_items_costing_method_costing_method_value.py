from enum import Enum


class SearchItemsCostingMethodCostingMethodValue(str, Enum):
    VALUE_0 = "_average"
    VALUE_1 = "_fifo"
    VALUE_2 = "_groupAverage"
    VALUE_3 = "_lifo"
    VALUE_4 = "_lotNumbered"
    VALUE_5 = "_serialized"
    VALUE_6 = "_standard"

    def __str__(self) -> str:
        return str(self.value)
