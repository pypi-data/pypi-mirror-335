from enum import Enum


class SearchItemsHazmatPackingGroupValue(str, Enum):
    I = "_i"
    II = "_ii"
    III = "_iii"

    def __str__(self) -> str:
        return str(self.value)
