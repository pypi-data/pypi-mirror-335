from enum import Enum


class SearchItemsHazmatPackingGroupHazmatPackingGroupValue(str, Enum):
    VALUE_0 = "_i"
    VALUE_1 = "_ii"
    VALUE_2 = "_iii"

    def __str__(self) -> str:
        return str(self.value)
