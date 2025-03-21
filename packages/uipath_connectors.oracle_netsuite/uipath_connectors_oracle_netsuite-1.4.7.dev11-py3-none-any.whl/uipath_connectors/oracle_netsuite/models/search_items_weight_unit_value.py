from enum import Enum


class SearchItemsWeightUnitValue(str, Enum):
    G = "_g"
    KG = "_kg"
    LB = "_lb"
    OZ = "_oz"

    def __str__(self) -> str:
        return str(self.value)
