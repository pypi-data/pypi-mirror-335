from enum import Enum


class SearchItemsMatrixTypeValue(str, Enum):
    CHILD = "_child"
    PARENT = "_parent"

    def __str__(self) -> str:
        return str(self.value)
