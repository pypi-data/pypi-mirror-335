from enum import Enum


class SearchItemsMatrixTypeMatrixTypeValue(str, Enum):
    VALUE_0 = "_parent"
    VALUE_1 = "_child"

    def __str__(self) -> str:
        return str(self.value)
