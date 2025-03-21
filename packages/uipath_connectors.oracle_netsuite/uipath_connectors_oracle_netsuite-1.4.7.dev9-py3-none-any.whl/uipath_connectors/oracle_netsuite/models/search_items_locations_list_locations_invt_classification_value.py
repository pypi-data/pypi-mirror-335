from enum import Enum


class SearchItemsLocationsListLocationsInvtClassificationValue(str, Enum):
    A = "_a"
    B = "_b"
    C = "_c"

    def __str__(self) -> str:
        return str(self.value)
