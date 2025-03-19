from enum import Enum


class SearchItemsInvtClassificationInvtClassificationValue(str, Enum):
    VALUE_0 = "_a"
    VALUE_1 = "_b"
    VALUE_2 = "_c"

    def __str__(self) -> str:
        return str(self.value)
