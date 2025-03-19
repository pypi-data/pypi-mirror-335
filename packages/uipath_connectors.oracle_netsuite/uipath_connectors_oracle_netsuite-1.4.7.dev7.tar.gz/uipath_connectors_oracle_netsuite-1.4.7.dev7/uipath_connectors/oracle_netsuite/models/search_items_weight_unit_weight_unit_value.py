from enum import Enum


class SearchItemsWeightUnitWeightUnitValue(str, Enum):
    VALUE_0 = "_g"
    VALUE_1 = "_kg"
    VALUE_2 = "_lb"
    VALUE_3 = "_oz"

    def __str__(self) -> str:
        return str(self.value)
